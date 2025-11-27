import pytest
from posts.models import Post


@pytest.mark.django_db
class TestPostQueries:

    def test_posts_query(self, graphql_client, user):
        """Test fetching posts"""
        Post.objects.create(author=user, content="Post 1")
        Post.objects.create(author=user, content="Post 2")

        query = """
            query {
                posts(page: 1, perPage: 10) {
                    id
                    content
                    author {
                        username
                    }
                }
            }
        """

        result = graphql_client.execute(query)
        assert "errors" not in result
        assert len(result["data"]["posts"]) == 2

    def test_post_query_by_id(self, graphql_client, post):
        """Test fetching single post"""
        query = f"""
            query {{
                post(id: "{post.id}") {{
                    id
                    content
                    author {{
                        username
                    }}
                }}
            }}
        """

        result = graphql_client.execute(query)
        assert "errors" not in result
        assert result["data"]["post"]["id"] == str(post.id)

    def test_user_posts_query(self, graphql_client, user, post):
        """Test fetching user's posts"""
        query = f"""
            query {{
                userPosts(userId: "{user.id}") {{
                    id
                    content
                }}
            }}
        """

        result = graphql_client.execute(query)
        assert "errors" not in result
        assert len(result["data"]["userPosts"]) == 1
