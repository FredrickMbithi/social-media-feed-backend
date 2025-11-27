import pytest


@pytest.fixture
def user(db, django_user_model):
    """Create a test user using the django_user_model fixture.

    Using `django_user_model` avoids importing `User` at module import time
    and lets pytest-django provide the user model configured for the project.
    """
    return django_user_model.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )


@pytest.fixture
def another_user(db, django_user_model):
    """Create another test user."""
    return django_user_model.objects.create_user(
        username="anotheruser",
        email="another@example.com",
        password="testpass123",
    )


@pytest.fixture
def post(db, user):
    """Create a test post. Import models lazily inside the fixture to avoid
    top-level Django model imports before Django is initialized by pytest-django.
    """
    from posts.models import Post

    return Post.objects.create(author=user, content="Test post content")


@pytest.fixture
def comment(db, post, user):
    """Create a test comment (lazy import)."""
    from posts.models import Comment

    return Comment.objects.create(post=post, author=user, content="Test comment")


@pytest.fixture
def graphql_client():
    """GraphQL test client. Import schema lazily."""
    from graphene.test import Client

    from socialfeed.schema import schema

    return Client(schema)
