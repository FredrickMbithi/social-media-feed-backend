from django.core.cache import cache
import hashlib

class CacheManager:
    """Centralized cache management for posts"""

    # Cache key prefixes
    POST_PREFIX = "post"
    POSTS_LIST_PREFIX = "posts_list"
    USER_POSTS_PREFIX = "user_posts"
    POST_COMMENTS_PREFIX = "post_comments"

    # Cache timeouts (in seconds)
    POST_TIMEOUT = 300  # 5 minutes
    LIST_TIMEOUT = 60  # 1 minute (lists change frequently)

    @staticmethod
    def _make_key(*args):
        """Generate cache key from arguments"""
        key_str = ":".join(str(arg) for arg in args)
        return hashlib.md5(key_str.encode()).hexdigest()

    @classmethod
    def get_post(cls, post_id):
        """Get cached post"""
        key = f"{cls.POST_PREFIX}:{post_id}"
        return cache.get(key)

    @classmethod
    def set_post(cls, post_id, post_data, timeout=None):
        """Cache post data"""
        key = f"{cls.POST_PREFIX}:{post_id}"
        timeout = timeout or cls.POST_TIMEOUT
        cache.set(key, post_data, timeout)

    @classmethod
    def invalidate_post(cls, post_id):
        """Invalidate post cache"""
        key = f"{cls.POST_PREFIX}:{post_id}"
        cache.delete(key)

    @classmethod
    def get_posts_list(cls, page, per_page, user_id=None, search=None):
        """Get cached posts list"""
        cache_key = cls._make_key(
            cls.POSTS_LIST_PREFIX, page, per_page, user_id or "", search or ""
        )
        return cache.get(cache_key)

    @classmethod
    def set_posts_list(cls, posts_data, page, per_page, user_id=None, search=None):
        """Cache posts list"""
        cache_key = cls._make_key(
            cls.POSTS_LIST_PREFIX, page, per_page, user_id or "", search or ""
        )
        cache.set(cache_key, posts_data, cls.LIST_TIMEOUT)

    @classmethod
    def invalidate_posts_lists(cls):
        """Invalidate all posts lists (call when new post created)"""
        # Pattern matching requires redis backend
        cache.delete_pattern(f"*{cls.POSTS_LIST_PREFIX}*")

    @classmethod
    def get_user_posts(cls, user_id):
        """Get cached user posts"""
        key = f"{cls.USER_POSTS_PREFIX}:{user_id}"
        return cache.get(key)

    @classmethod
    def set_user_posts(cls, user_id, posts_data):
        """Cache user posts"""
        key = f"{cls.USER_POSTS_PREFIX}:{user_id}"
        cache.set(key, posts_data, cls.LIST_TIMEOUT)

    @classmethod
    def invalidate_user_posts(cls, user_id):
        """Invalidate user posts cache"""
        key = f"{cls.USER_POSTS_PREFIX}:{user_id}"
        cache.delete(key)


def cache_post_data(post):
    """Convert post to cacheable dict"""
    return {
        "id": post.id,
        "author_id": post.author_id,
        "author_username": post.author.username,
        "content": post.content,
        "image_url": post.image_url,
        "likes_count": post.likes_count,
        "comments_count": post.comments_count,
        "shares_count": post.shares_count,
        "created_at": post.created_at.isoformat(),
        "updated_at": post.updated_at.isoformat(),
    }
