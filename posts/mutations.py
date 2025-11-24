import graphene
from graphql_jwt.decorators import login_required
from django.db.models import F
from .models import Post, Comment, Interaction
from .types import PostType, CommentType
from .cache_utils import CacheManager


class CreatePost(graphene.Mutation):
    """Create a new post"""
    post = graphene.Field(PostType)
    
    class Arguments:
        content = graphene.String(required=True)
        image_url = graphene.String()
    
    @login_required
    def mutate(self, info, content, image_url=None):
        user = info.context.user
        
        # Validation
        if not content or len(content.strip()) == 0:
            raise Exception('Post content cannot be empty')
        
        if len(content) > 5000:
            raise Exception('Post content too long (max 5000 characters)')
        
        # Create post
        post = Post.objects.create(
            author=user,
            content=content.strip(),
            image_url=image_url
        )
        
        # Invalidate caches
        CacheManager.invalidate_posts_lists()
        CacheManager.invalidate_user_posts(user.id)

        return CreatePost(post=post)


class UpdatePost(graphene.Mutation):
    """Update an existing post"""
    post = graphene.Field(PostType)
    
    class Arguments:
        post_id = graphene.ID(required=True)
        content = graphene.String()
        image_url = graphene.String()
    
    @login_required
    def mutate(self, info, post_id, content=None, image_url=None):
        user = info.context.user
        
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            raise Exception('Post not found')
        
        # Permission check
        if post.author != user:
            raise Exception('You can only edit your own posts')
        
        # Update fields
        if content is not None:
            if len(content.strip()) == 0:
                raise Exception('Post content cannot be empty')
            post.content = content.strip()
        
        if image_url is not None:
            post.image_url = image_url
        
        post.save()
        # Invalidate caches
        CacheManager.invalidate_post(post_id)
        CacheManager.invalidate_posts_lists()

        return UpdatePost(post=post)


class DeletePost(graphene.Mutation):
    """Delete a post"""
    success = graphene.Boolean()
    message = graphene.String()
    
    class Arguments:
        post_id = graphene.ID(required=True)
    
    @login_required
    def mutate(self, info, post_id):
        user = info.context.user
        
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            raise Exception('Post not found')
        
        # Permission check
        if post.author != user:
            raise Exception('You can only delete your own posts')
        
        author_id = post.author_id
        post.delete()
        
        # Invalidate caches
        CacheManager.invalidate_post(post_id)
        CacheManager.invalidate_posts_lists()
        CacheManager.invalidate_user_posts(author_id)

        return DeletePost(success=True, message='Post deleted successfully')


class CreateComment(graphene.Mutation):
    """Add a comment to a post"""
    comment = graphene.Field(CommentType)
    
    class Arguments:
        post_id = graphene.ID(required=True)
        content = graphene.String(required=True)
    
    @login_required
    def mutate(self, info, post_id, content):
        user = info.context.user
        
        # Validation
        if not content or len(content.strip()) == 0:
            raise Exception('Comment content cannot be empty')
        
        if len(content) > 1000:
            raise Exception('Comment too long (max 1000 characters)')
        
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            raise Exception('Post not found')
        
        # Create comment
        comment = Comment.objects.create(
            post=post,
            author=user,
            content=content.strip()
        )
        
        # Update post comment count atomically
        Post.objects.filter(pk=post_id).update(
            comments_count=F('comments_count') + 1
        )
        
        return CreateComment(comment=comment)


class DeleteComment(graphene.Mutation):
    """Delete a comment"""
    success = graphene.Boolean()
    message = graphene.String()
    
    class Arguments:
        comment_id = graphene.ID(required=True)
    
    @login_required
    def mutate(self, info, comment_id):
        user = info.context.user
        
        try:
            comment = Comment.objects.select_related('post').get(pk=comment_id)
        except Comment.DoesNotExist:
            raise Exception('Comment not found')
        
        # Permission check (author or post author can delete)
        if comment.author != user and comment.post.author != user:
            raise Exception('You can only delete your own comments')
        
        post_id = comment.post.id
        comment.delete()
        
        # Update post comment count
        Post.objects.filter(pk=post_id).update(
            comments_count=F('comments_count') - 1
        )
        
        return DeleteComment(success=True, message='Comment deleted successfully')


class LikePost(graphene.Mutation):
    """Like or unlike a post"""
    post = graphene.Field(PostType)
    liked = graphene.Boolean()
    
    class Arguments:
        post_id = graphene.ID(required=True)
    
    @login_required
    def mutate(self, info, post_id):
        user = info.context.user
        
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            raise Exception('Post not found')
        
        # Toggle like
        interaction, created = Interaction.objects.get_or_create(
            post=post,
            user=user,
            interaction_type='like'
        )
        
        if created:
            # New like
            Post.objects.filter(pk=post_id).update(
                likes_count=F('likes_count') + 1
            )
            liked = True
        else:
            # Unlike
            interaction.delete()
            Post.objects.filter(pk=post_id).update(
                likes_count=F('likes_count') - 1
            )
            liked = False
        
        post.refresh_from_db()
        # Invalidate post cache
        CacheManager.invalidate_post(post_id)
        return LikePost(post=post, liked=liked)


class SharePost(graphene.Mutation):
    """Share a post"""
    post = graphene.Field(PostType)
    shared = graphene.Boolean()
    
    class Arguments:
        post_id = graphene.ID(required=True)
    
    @login_required
    def mutate(self, info, post_id):
        user = info.context.user
        
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            raise Exception('Post not found')
        
        # Toggle share
        interaction, created = Interaction.objects.get_or_create(
            post=post,
            user=user,
            interaction_type='share'
        )
        
        if created:
            # New share
            Post.objects.filter(pk=post_id).update(
                shares_count=F('shares_count') + 1
            )
            shared = True
        else:
            # Unshare
            interaction.delete()
            Post.objects.filter(pk=post_id).update(
                shares_count=F('shares_count') - 1
            )
            shared = False
        
        post.refresh_from_db()
        return SharePost(post=post, shared=shared)


class Mutation(graphene.ObjectType):
    create_post = CreatePost.Field()
    update_post = UpdatePost.Field()
    delete_post = DeletePost.Field()
    create_comment = CreateComment.Field()
    delete_comment = DeleteComment.Field()
    like_post = LikePost.Field()
    share_post = SharePost.Field()