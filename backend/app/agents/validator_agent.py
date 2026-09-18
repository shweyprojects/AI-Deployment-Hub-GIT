from typing import Dict, Any

from app.services.validator_service import ValidatorService


class ValidatorAgent:
    """
    Agent responsible for orchestrating deployment validation.
    """

    def __init__(self):
        self.service = ValidatorService()

    def validate(
        self,
        project_path: str,
        deployment_plan: Dict[str, Any],
    ) -> Dict[str, Any]:

        if not project_path:
            raise ValueError("Project path is required.")

        if not deployment_plan:
            raise ValueError("Deployment plan is required.")

        return self.service.validate(
            project_path=project_path,
            deployment_plan=deployment_plan,
        )