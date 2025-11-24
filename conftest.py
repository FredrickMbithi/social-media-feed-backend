import pytest
from django.contrib.auth.models import User
from posts.models import Post, Comment, Interaction

@pytest.fixture
def user(db):
    """Create a test user"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def another_user(db):
    """Create another test user"""
    return User.objects.create_user(
        username='anotheruser',
        email='another@example.com',
        password='testpass123'
    )


@pytest.fixture
def post(db, user):
    """Create a test post"""
    return Post.objects.create(
        author=user,
        content='Test post content'
    )


@pytest.fixture
def comment(db, post, user):
    """Create a test comment"""
    return Comment.objects.create(
        post=post,
        author=user,
        content='Test comment'
    )


@pytest.fixture
def graphql_client():
    """GraphQL test client"""
    from graphene.test import Client
    from socialfeed.schema import schema
    return Client(schema)
