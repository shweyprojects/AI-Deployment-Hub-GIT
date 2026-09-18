from typing import Dict, Any

from app.services.docker_run_service import DockerRunService


class DockerRunAgent:
    """
    Agent responsible for orchestrating Docker container execution.
    """

    def __init__(self):
        self.service = DockerRunService()

    def run(
        self,
        image_name: str,
        container_name: str,
        port: int,
    ) -> Dict[str, Any]:

        if not image_name:
            raise ValueError("Docker image name is required.")

        if not container_name:
            raise ValueError("Docker container name is required.")

        if not port:
            raise ValueError("Application port is required.")

        return self.service.run(
            image_name=image_name,
            container_name=container_name,
            port=port,
        )