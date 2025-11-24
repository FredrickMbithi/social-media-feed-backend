import re
from django.utils.html import escape
from graphql import GraphQLError


class SecurityValidator:
    """Security validation utilities"""
    
    @staticmethod
    def validate_content(content):
        """Validate and sanitize text content"""
        if not content:
            raise GraphQLError('Content cannot be empty')
        
        # Remove excessive whitespace
        content = ' '.join(content.split())
        
        # Check for SQL injection patterns (basic detection)
        sql_patterns = [
            r'(\bUNION\b.*\bSELECT\b)',
            r'(\bDROP\b.*\bTABLE\b)',
            r'(\bINSERT\b.*\bINTO\b)',
            r'(--\s)',
            r'(;\s*DROP)',
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                raise GraphQLError('Invalid content detected')
        
        # Escape HTML to prevent XSS
        content = escape(content)
        
        return content
    
    @staticmethod
    def validate_url(url):
        """Validate image URL"""
        if not url:
            return None
        
        # Basic URL validation
        url_pattern = r'^https?://.+'
        if not re.match(url_pattern, url):
            raise GraphQLError('Invalid URL format')
        
        # Block dangerous protocols
        if url.lower().startswith(('javascript:', 'data:', 'vbscript:', 'file:')):
            raise GraphQLError('Invalid URL protocol')
        
        # Check max length
        if len(url) > 2048:
            raise GraphQLError('URL too long')
        
        return url
