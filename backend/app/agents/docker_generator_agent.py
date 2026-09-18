from typing import Dict, Any

from app.services.docker_generator_service import DockerGeneratorService


class DockerGeneratorAgent:
    """
    Agent responsible for orchestrating Docker artifact generation.
    """

    def __init__(self):
        self.service = DockerGeneratorService()

    def generate(
        self,
        project_path: str,
        deployment_plan: Dict[str, Any],
    ) -> Dict[str, Any]:
        if not project_path:
            raise ValueError("Project path is required.")

        if not deployment_plan:
            raise ValueError("Deployment plan is required.")

        return self.service.generate(
            project_path=project_path,
            deployment_plan=deployment_plan,
        )