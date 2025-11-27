import pytest
from posts.security import SecurityValidator
from graphql import GraphQLError


class TestSecurityValidator:

    def test_validate_content_removes_whitespace(self):
        """Test excessive whitespace is removed"""
        content = "Hello    world   test"
        result = SecurityValidator.validate_content(content)
        assert result == "Hello world test"

    def test_validate_content_blocks_sql_injection(self):
        """Test SQL injection patterns are blocked"""
        with pytest.raises(GraphQLError, match="Invalid content"):
            SecurityValidator.validate_content("'; DROP TABLE posts; --")

    def test_validate_content_escapes_html(self):
        """Test HTML is escaped to prevent XSS"""
        content = "<script>alert('xss')</script>"
        result = SecurityValidator.validate_content(content)
        assert "<script>" not in result
        assert "&lt;script&gt;" in result

    def test_validate_url_blocks_javascript(self):
        """Test javascript: protocol is blocked"""
        with pytest.raises(GraphQLError, match="Invalid URL protocol"):
            SecurityValidator.validate_url("javascript:alert('xss')")

    def test_validate_url_allows_https(self):
        """Test valid HTTPS URLs are allowed"""
        url = "https://example.com/image.jpg"
        result = SecurityValidator.validate_url(url)
        assert result == url
