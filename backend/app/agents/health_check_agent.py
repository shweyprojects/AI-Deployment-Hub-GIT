from typing import Dict, Any

from app.services.health_check_service import HealthCheckService


class HealthCheckAgent:
    """
    Agent responsible for orchestrating application health checks.
    """

    def __init__(self):
        self.service = HealthCheckService()

    def check(
        self,
        url: str,
        retries: int = 5,
        delay: int = 2,
    ) -> Dict[str, Any]:

        if not url:
            raise ValueError("Health check URL is required.")

        return self.service.check(
            url=url,
            retries=retries,
            delay=delay,
        )