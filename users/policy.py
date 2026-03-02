from django.conf import settings


class RateLimitPolicy:
    """
    Decides rate limit rules for a request.
    """

    @classmethod
    def for_request(cls, request):
        path = request.path
        user = request.user
        window = settings.RATE_LIMIT_WINDOW

        if path.startswith("/login/"):
            return (10 if user.is_authenticated else 5), window

        if path.startswith("/search/"):
            return (30 if user.is_authenticated else 10), window

        return (20 if user.is_authenticated else 10), window