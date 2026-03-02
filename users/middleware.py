from django.http import JsonResponse

from .redis_client import redis_client
from .policy import RateLimitPolicy
from .abuse_engine import AbuseEngine
from .decisions import EnforcementDecision
from .logger import logger


class RateLimitMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        identity = self.get_identity(request)

        # phase 4: enforcement FIRST
        decision, cooldown = EnforcementDecision.get_decision(identity)
        if decision == "cooldown":
            key = f"cooldown:{identity}"

            if not redis_client.exists(key):
                redis_client.setex(key, cooldown, 1)

            logger.warning(
                "cooldown_applied",
                extra={
                    "identity": identity,
                    "cooldown_seconds": cooldown,
                },
            )

            return JsonResponse(
                {
                    "detail": "Temporarily blocked due to suspicious activity",
                    "retry_after": cooldown,
                },
                status=429,
            )

        #  Phase 2: policy
        limit, window = RateLimitPolicy.for_request(request)
        key = self.build_redis_key(identity, request.path)

        try:
            count = redis_client.incr(key)

            if count == 1:
                redis_client.expire(key, window)

            if count > limit:
                #  Observability metric
                redis_client.incr("metrics:rate_limit_hits")

                # Phase 3: abuse signal
                AbuseEngine.record_event(identity, "rate_limit_hit")

                logger.info(
                    "rate_limit_hit",
                    extra={
                        "identity": identity,
                        "path": request.path,
                        "count": count,
                        "limit": limit,
                    },
                )

                return JsonResponse(
                    {"detail": "Rate limit exceeded"},
                    status=429,
                )

        except Exception as e:
            logger.error(
                "rate_limit_redis_error",
                extra={"error": str(e)},
            )
            # FAIL-OPEN

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