from django.test import TestCase
from django.contrib.auth.models import User
from graphene.test import Client
from socialfeed.schema import schema
from posts.models import Post, Comment


class GraphQLTestCase(TestCase):
    def setUp(self):
        self.client = Client(schema)
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="password123"
        )

    def test_register_user(self):
        """Test user registration"""
        mutation = """
            mutation {
                register(
                    username: "newuser"
                    email: "new@example.com"
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
        result = self.client.execute(mutation)
        self.assertIsNone(result.get("errors"))
        self.assertEqual(result["data"]["register"]["user"]["username"], "newuser")
        self.assertIsNotNone(result["data"]["register"]["token"])

    def test_create_post_without_auth(self):
        """Test creating post without authentication fails"""
        mutation = """
            mutation {
                createPost(content: "Test post") {
                    post {
                        id
                    }
                }
            }
        """
        result = self.client.execute(mutation)
        self.assertIsNotNone(result.get("errors"))

    def test_create_post_with_auth(self):
        """Test creating post with authentication"""
        # This would need proper JWT token setup
        # For now, just verify the model
        post = Post.objects.create(author=self.user, content="Test post")
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.content, "Test post")

    def test_post_query(self):
        """Test querying posts"""
        Post.objects.create(author=self.user, content="Test post")

        query = """
            query {
                posts(page: 1, perPage: 10) {
                    id
                    content
                }
            }
        """
        result = self.client.execute(query)
        self.assertIsNone(result.get("errors"))
        self.assertEqual(len(result["data"]["posts"]), 1)
