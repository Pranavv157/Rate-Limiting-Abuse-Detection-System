from django.conf import settings


class RateLimitPolicy:
    """
    Decides rate limit rules for a request.
    This class does NOT talk to Redis.
    """

    DEFAULT_WINDOW = settings.RATE_LIMIT_WINDOW

    @classmethod
    def for_request(cls, request):
        """
        Returns (limit, window_seconds)
        """
        path = request.path
        user = request.user

        #  Login endpoint (sensitive)
        if path.startswith("/login/"):
            if user.is_authenticated:
                return 10, cls.DEFAULT_WINDOW
            return 5, cls.DEFAULT_WINDOW

        #  Search endpoint
        if path.startswith("/search/"):
            if user.is_authenticated:
                return 30, cls.DEFAULT_WINDOW
            return 10, cls.DEFAULT_WINDOW

        #  Default fallback
        if user.is_authenticated:
            return 20, cls.DEFAULT_WINDOW

        return 10, cls.DEFAULT_WINDOW