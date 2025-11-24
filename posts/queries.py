import graphene
from graphene import relay
from django.db.models import Q, Prefetch, Case, When
from .types import PostType, CommentType
from .models import Post, Comment
from .cache_utils import CacheManager, cache_post_data


class Query(graphene.ObjectType):
    posts = graphene.List(
        PostType,
        page=graphene.Int(default_value=1),
        per_page=graphene.Int(default_value=10),
        user_id=graphene.Int(required=False),
        search=graphene.String(required=False)
    )
    post = graphene.Field(PostType, id=graphene.ID(required=True))
    user_posts = graphene.List(PostType, user_id=graphene.ID(required=True))
    me = graphene.Field('posts.types.UserType')
    user = graphene.Field('posts.types.UserType', id=graphene.ID(required=True))

    def resolve_posts(self, info, page=1, per_page=10, user_id=None, search=None):
        """
        Fetch posts with caching and optimized queries
        """
        # Try cache first
        cached = CacheManager.get_posts_list(page, per_page, user_id, search)
        if cached:
            post_ids = cached
            # Preserve order using CASE WHEN
            preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(post_ids)])
            return Post.objects.filter(id__in=post_ids)\
                .select_related('author')\
                .prefetch_related(Prefetch('comments', queryset=Comment.objects.select_related('author').order_by('-created_at')))\
                .order_by(preserved_order)
        
        # Build optimized query
        qs = Post.objects.select_related('author').prefetch_related(
            Prefetch('comments', queryset=Comment.objects.select_related('author')[:5])
        )
        
        # Filters
        if user_id:
            qs = qs.filter(author_id=user_id)
        
        if search:
            qs = qs.filter(Q(content__icontains=search))
        
        # Pagination
        start = (page - 1) * per_page
        end = start + per_page
        
        posts = list(qs[start:end])
        
        # Cache post IDs
        post_ids = [post.id for post in posts]
        CacheManager.set_posts_list(post_ids, page, per_page, user_id, search)
        
        return posts

    def resolve_post(self, info, id):
        """
        Fetch single post with caching
        """
        # Try cache first
        cached = CacheManager.get_post(id)
        if cached:
            # Reconstruct from cache (simplified)
            try:
                return Post.objects.select_related('author').prefetch_related(
                    Prefetch('comments', queryset=Comment.objects.select_related('author'))
                ).get(pk=id)
            except Post.DoesNotExist:
                CacheManager.invalidate_post(id)
                return None
        
        # Fetch with optimized query
        try:
            post = Post.objects.select_related('author').prefetch_related(
                Prefetch('comments', queryset=Comment.objects.select_related('author')),
                'interactions__user'
            ).get(pk=id)
            
            # Cache it
            CacheManager.set_post(id, cache_post_data(post))
            return post
        except Post.DoesNotExist:
            return None

    def resolve_user_posts(self, info, user_id):
        """
        Fetch user posts with caching
        """
        cached = CacheManager.get_user_posts(user_id)
        if cached:
            post_ids = cached
            preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(post_ids)])
            return Post.objects.filter(id__in=post_ids).select_related('author').order_by(preserved_order)
        
        posts = list(
            Post.objects.filter(author_id=user_id)
            .select_related('author')
            .prefetch_related('comments__author')
        )
        
        # Cache post IDs
        post_ids = [post.id for post in posts]
        CacheManager.set_user_posts(user_id, post_ids)
        
        return posts
    
    def resolve_me(self, info):
        """Get current authenticated user"""
        user = info.context.user
        if user.is_authenticated:
            return user
        return None
    
    def resolve_user(self, info, id):
        """Get user by ID"""
        from django.contrib.auth.models import User
        try:
            return User.objects.get(pk=id)
        except User.DoesNotExist:
            return None