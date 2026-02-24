from django.http import JsonResponse
from .redis_client import redis_client
from .policy import RateLimitPolicy
from .abuse_engine import AbuseEngine

class RateLimitMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        identity = self.get_identity(request)
        limit, window = RateLimitPolicy.for_request(request)
        key = self.build_redis_key(identity, request.path)

        try:
            count = redis_client.incr(key)
            if count == 1:
                redis_client.expire(key, window)

            if count > limit:
                if count > limit:
                    AbuseEngine.record_event(identity, "rate_limit_hit")
                    return JsonResponse(
                        {"detail": "Rate limit exceeded"},
                        status=429,
                    )

        except Exception:
            # FAIL-OPEN
            pass

        return self.get_response(request)

    def get_identity(self, request):
        if request.user.is_authenticated:
            return f"user:{request.user.id}"
        return f"ip:{self.get_client_ip(request)}"

    def build_redis_key(self, identity, path):
        return f"rate_limit:{identity}:{path}"

    def get_client_ip(self, request):
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            return xff.split(",")[0]
        return request.META.get("REMOTE_ADDR")