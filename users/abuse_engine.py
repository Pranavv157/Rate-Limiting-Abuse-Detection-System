from .redis_client import redis_client
from .logger import logger


class AbuseEngine:
    """
    Tracks and scores suspicious behavior over time.
    """

    # Abuse score decays automatically via Redis TTL
    DECAY_WINDOW = 300  # seconds (5 minutes)

    # How much each event contributes to abuse score
    EVENT_SCORES = {
        "rate_limit_hit": 2,
        "failed_login": 3,
        "unauthorized": 1,
    }

    @classmethod
    def record_event(cls, identity, event):
        score = cls.EVENT_SCORES.get(event)
        if not score:
            return

        key = f"abuse_score:{identity}"

        try:
            pipeline = redis_client.pipeline()
            pipeline.incrby(key, score)
            pipeline.expire(key, cls.DECAY_WINDOW)
            pipeline.execute()

            logger.info(
                "abuse_event",
                extra={
                    "identity": identity,
                    "event": event,
                    "score_added": score,
                },
            )

        except Exception as e:
            # Fail-open: abuse tracking should never break requests
            logger.error(
                "abuse_engine_error",
                extra={
                    "identity": identity,
                    "event": event,
                    "error": str(e),
                },
            )

    @classmethod
    def get_score(cls, identity):
        value = redis_client.get(f"abuse_score:{identity}")
        return int(value) if value else 0