from django_ratelimit.decorators import ratelimit
from functools import wraps
from graphql import GraphQLError


def rate_limit(group=None, key="user_or_ip", rate="10/m", method="ALL"):
    """
    Rate limit decorator for GraphQL resolvers
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, info, *args, **kwargs):
            # Get request from info context
            request = info.context

            # Apply rate limit
            limiter = ratelimit(group=group, key=key, rate=rate, method=method)
            limited_func = limiter(lambda r: True)

            # Check if rate limited
            is_limited = limited_func(request)

            if getattr(request, "limited", False):
                raise GraphQLError("Rate limit exceeded. Please try again later.")

            return func(self, info, *args, **kwargs)

        return wrapper

    return decorator
