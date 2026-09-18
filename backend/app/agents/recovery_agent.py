from typing import Dict, Any
from urllib.parse import urlparse

from app.services.docker_run_service import DockerRunService
from app.services.health_check_service import HealthCheckService


class RecoveryAgent:
    """
    Agent responsible for recovering failed deployments.

    Strategy:
    1. Restart the Docker container.
    2. Run a health check.
    3. Retry up to the configured number of attempts.
    """

    def __init__(self):
        self.docker_run_service = DockerRunService()
        self.health_check_service = HealthCheckService()

    def recover(
        self,
        image_name: str,
        container_name: str,
        port: int,
        health_url: str,
        max_retries: int = 3,
    ) -> Dict[str, Any]:

        if not image_name:
            raise ValueError("Docker image name is required.")

        if not container_name:
            raise ValueError("Docker container name is required.")

        if not port:
            raise ValueError("Application port is required.")

        if not health_url:
            raise ValueError("Health check URL is required.")

        attempts = []

        for attempt in range(1, max_retries + 1):

            run_result = self.docker_run_service.run(
                image_name=image_name,
                container_name=container_name,
                port=port,
            )

            parsed_health_url = urlparse(health_url)
            recovery_health_url = (
                f"{run_result.get('url', '').rstrip('/')}"
                f"{parsed_health_url.path or '/'}"
            )

            health_result = self.health_check_service.check(
                url=recovery_health_url,
                retries=3,
                delay=2,
            )

            attempt_result = {
                "attempt": attempt,
                "run": run_result,
                "health_check": health_result,
            }

            attempts.append(attempt_result)

            if health_result.get("healthy") is True:
                return {
                    "status": "success",
                    "recovered": True,
                    "attempts": attempts,
                    "container_name": container_name,
                    "url": recovery_health_url,
                }

        return {
            "status": "failed",
            "recovered": False,
            "attempts": attempts,
            "container_name": container_name,
            "url": recovery_health_url,
            "error": "Deployment could not be recovered.",
        }
