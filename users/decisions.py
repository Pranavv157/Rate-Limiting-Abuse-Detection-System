from .abuse_engine import AbuseEngine
from .redis_client import redis_client


class EnforcementDecision:
    """
    Decides what action to take based on abuse score.
    """

    COOLDOWN_THRESHOLDS = {
        7: 60,     # 1 minute block
        10: 300,   # 5 minutes block
    }

    @classmethod
    def get_decision(cls, identity):
        score = AbuseEngine.get_score(identity)

        for threshold, cooldown in sorted(
            cls.COOLDOWN_THRESHOLDS.items(), reverse=True
        ):
            if score >= threshold:
                return "cooldown", cooldown

        return "allow", None