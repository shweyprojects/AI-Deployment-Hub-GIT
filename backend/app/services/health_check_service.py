import time
from typing import Dict, Any

import requests


class HealthCheckService:
    """
    Checks whether the deployed application is healthy.
    """

    def check(
        self,
        url: str,
        retries: int = 5,
        delay: int = 2,
    ) -> Dict[str, Any]:

        if not url:
            raise ValueError("Health check URL is required.")

        attempts = []

        for attempt in range(1, retries + 1):
            try:
                response = requests.get(
                    url,
                    timeout=5,
                )

                attempts.append({
                    "attempt": attempt,
                    "status_code": response.status_code,
                })

                if 200 <= response.status_code < 400:
                    return {
                        "status": "success",
                        "healthy": True,
                        "url": url,
                        "status_code": response.status_code,
                        "attempts": attempts,
                    }

            except requests.RequestException as exc:
                attempts.append({
                    "attempt": attempt,
                    "error": str(exc),
                })

            if attempt < retries:
                time.sleep(delay)

        return {
            "status": "failed",
            "healthy": False,
            "url": url,
            "attempts": attempts,
        }