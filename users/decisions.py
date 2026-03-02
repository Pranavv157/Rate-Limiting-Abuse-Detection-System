from .abuse_engine import AbuseEngine


class EnforcementDecision:
    """
    Decides what action to take based on abuse score.
    """

    # threshold → cooldown seconds
    COOLDOWN_THRESHOLDS = {
        10: 300,  # 5 minutes
        7: 60,    # 1 minute
    }

    @classmethod
    def get_decision(cls, identity):
        score = AbuseEngine.get_score(identity)

        for threshold, cooldown in cls.COOLDOWN_THRESHOLDS.items():
            if score >= threshold:
                return "cooldown", cooldown

        return "allow", None