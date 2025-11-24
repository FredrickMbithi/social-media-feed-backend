import pytest
from django.db.models import F
from posts.models import Post, Comment, Interaction

@pytest.mark.django_db
class TestPostModel:
    
    def test_create_post(self, user):
        """Test creating a post"""
        post = Post.objects.create(
            author=user,
            content='Test content'
        )
        assert post.author == user
        assert post.content == 'Test content'
        assert post.likes_count == 0
        assert post.comments_count == 0
    
    def test_post_like_atomic(self, user, another_user, post):
        """Test atomic like operation"""
        # User 1 likes
        interaction1, created1 = Interaction.objects.get_or_create(
            post=post,
            user=user,
            interaction_type='like'
        )
        Post.objects.filter(pk=post.pk).update(likes_count=F('likes_count') + 1)
        
        # User 2 likes
        interaction2, created2 = Interaction.objects.get_or_create(
            post=post,
            user=another_user,
            interaction_type='like'
        )
        Post.objects.filter(pk=post.pk).update(likes_count=F('likes_count') + 1)
        
        post.refresh_from_db()
        assert post.likes_count == 2
        assert Interaction.objects.filter(post=post, interaction_type='like').count() == 2
    
    def test_post_ordering(self, user):
        """Test posts are ordered by created_at descending"""
        post1 = Post.objects.create(author=user, content='First')
        post2 = Post.objects.create(author=user, content='Second')
        
        posts = list(Post.objects.all())
        assert posts[0] == post2  # Most recent first
        assert posts[1] == post1

@pytest.mark.django_db
class TestCommentModel:
    
    def test_create_comment(self, post, user):
        """Test creating a comment"""
        comment = Comment.objects.create(
            post=post,
            author=user,
            content='Test comment'
        )
        assert comment.post == post
        assert comment.author == user
        assert comment.content == 'Test comment'
    
    def test_comment_count_update(self, post, user):
        """Test comment count updates"""
        initial_count = post.comments_count
        
        Comment.objects.create(post=post, author=user, content='Comment 1')
        Post.objects.filter(pk=post.pk).update(comments_count=F('comments_count') + 1)
        
        post.refresh_from_db()
        assert post.comments_count == initial_count + 1
