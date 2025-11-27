import pytest
from django.contrib.auth.models import User
from posts.models import Post
@pytest.mark.django_db
class TestAuthMutations:

    def test_register_user(self, graphql_client):
        """Test user registration"""
        mutation = """
        mutation {
            register(
                username: "newuser",
                email: "new@example.com",
                password: "password123"
            ) {
                user {
                    username
                    email
                }
                token
            }
        }
        """
        result = graphql_client.execute(mutation)
        assert "errors" not in result
        assert result["data"]["register"]["user"]["username"] == "newuser"
        assert result["data"]["register"]["token"] is not None

        # Verify user created
        assert User.objects.filter(username="newuser").exists()

    def test_register_duplicate_username(self, graphql_client, user):
        """Test registration with existing username fails"""
        mutation = f"""
            mutation {{
                register(
                    username: "{user.username}",
                    email: "different@example.com",
                    password: "password123"
                ) {{
                    user {{
                        username
                    }}
                }}
            }}
        """

        result = graphql_client.execute(mutation)
        assert "errors" in result


@pytest.mark.django_db
class TestPostMutations:
    def test_create_post_requires_auth(self, graphql_client):
        """Test creating post without auth fails"""
        mutation = """
            mutation {
                createPost(content: "Test post") {
                    post {
                        id
                    }
                }
            }
        """

        result = graphql_client.execute(mutation)
        assert "errors" in result

    def test_delete_post_permission(self, user, another_user):
        """Test users can only delete their own posts"""
        post = Post.objects.create(author=user, content="Test")

        # Try to delete another user's post
        from posts.mutations import DeletePost

        class MockInfo:
            class context:
                user = another_user

        with pytest.raises(Exception, match="You can only delete your own posts"):
            DeletePost.mutate(None, MockInfo(), post_id=post.id)
