import time
from .redis_client import redis_client


class AbuseEngine:
    """
    Tracks and scores suspicious behavior.
    """

    DECAY_WINDOW = 300  # seconds (5 min)
    DECAY_AMOUNT = 1

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

        pipeline = redis_client.pipeline()
        pipeline.incrby(key, score)
        pipeline.expire(key, cls.DECAY_WINDOW)
        pipeline.execute()

    @classmethod
    def get_score(cls, identity):
        value = redis_client.get(f"abuse_score:{identity}")
        return int(value) if value else 0