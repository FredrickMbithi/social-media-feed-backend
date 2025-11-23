import graphene
from graphene import relay
from graphene_django.filter import DjangoFilterBackend
from django.db.models import Q
from .types import PostType, CommentType
from .models import Post, Comment


class Query(graphene.ObjectType):
    # List all posts with pagination
    posts = graphene.List(
        PostType,
        page=graphene.Int(default_value=1),
        per_page=graphene.Int(default_value=10),
        user_id=graphene.Int(required=False),
        search=graphene.String(required=False)
    )
    
    # Single post by ID
    post = graphene.Field(PostType, id=graphene.ID(required=True))
    
    # User's posts
    user_posts = graphene.List(
        PostType,
        user_id=graphene.ID(required=True)
    )

    def resolve_posts(self, info, page=1, per_page=10, user_id=None, search=None):
        """
        Fetch posts with pagination and optional filters
        """
        qs = Post.objects.select_related('author').prefetch_related(
            'comments__author'
        )
        
        # Filter by user if provided
        if user_id:
            qs = qs.filter(author_id=user_id)
        
        # Search in content
        if search:
            qs = qs.filter(Q(content__icontains=search))
        
        # Pagination
        start = (page - 1) * per_page
        end = start + per_page
        
        return qs[start:end]

    def resolve_post(self, info, id):
        """
        Fetch single post by ID with optimized queries
        """
        try:
            return Post.objects.select_related('author').prefetch_related(
                'comments__author',
                'interactions__user'
            ).get(pk=id)
        except Post.DoesNotExist:
            return None

    def resolve_user_posts(self, info, user_id):
        """
        Fetch all posts by a specific user
        """
        return Post.objects.filter(author_id=user_id).select_related('author')