from typing import Dict, Any

from app.services.docker_build_service import DockerBuildService


class DockerBuildAgent:
    """
    Agent responsible for orchestrating Docker image building.
    """

    def __init__(self):
        self.service = DockerBuildService()

    def build(
        self,
        project_path: str,
        image_name: str,
    ) -> Dict[str, Any]:

        if not project_path:
            raise ValueError("Project path is required.")

        if not image_name:
            raise ValueError("Docker image name is required.")

        return self.service.build(
            project_path=project_path,
            image_name=image_name,
        )