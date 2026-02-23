import time
from django.conf import settings
from django.http import JsonResponse
from .redis_client import redis_client


class RateLimitMiddleware:
    """
    Fixed-window rate limiting using Redis INCR + EXPIRE.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.window = settings.RATE_LIMIT_WINDOW
        self.limit = settings.RATE_LIMIT_REQUESTS

    def __call__(self, request):
        identity = self.get_identity(request)
        key = self.build_redis_key(identity)

        try:
            count = redis_client.incr(key)

            # First request in the window → set TTL
            if count == 1:
                redis_client.expire(key, self.window)

            if count > self.limit:
                return JsonResponse(
                    {
                        "detail": "Rate limit exceeded",
                        "limit": self.limit,
                        "window_seconds": self.window,
                    },
                    status=429,
                )

        except Exception:
            # FAIL-OPEN strategy (very important)
            # If Redis is down, do NOT block traffic
            pass

        return self.get_response(request)

    def get_identity(self, request):
        """
        Identify the caller:
        - authenticated user → user_id
        - anonymous → IP address
        """
        if request.user.is_authenticated:
            return f"user:{request.user.id}"
        return f"ip:{self.get_client_ip(request)}"

    def build_redis_key(self, identity):
        return f"rate_limit:{identity}"

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")