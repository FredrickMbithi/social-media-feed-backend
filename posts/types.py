import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth.models import User
from .models import Post, Comment, Interaction


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username", "email", "date_joined")


class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = ("id", "post", "author", "content", "created_at")


class InteractionType(DjangoObjectType):
    class Meta:
        model = Interaction
        fields = ("id", "post", "user", "interaction_type", "created_at")


class PostType(DjangoObjectType):
    comments = graphene.List(CommentType)

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "content",
            "image_url",
            "likes_count",
            "comments_count",
            "shares_count",
            "created_at",
            "updated_at",
        )

    def resolve_comments(self, info):
        # Optimized: only fetch recent comments
        return self.comments.select_related("author").all()[:10]
