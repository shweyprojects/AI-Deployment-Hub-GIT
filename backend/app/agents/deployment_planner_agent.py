from app.services.deployment_planner_service import (
    DeploymentPlannerService
)


class DeploymentPlannerAgent:

    def __init__(self):
        self.planner_service = DeploymentPlannerService()

    def execute(
        self,
        project_structure: dict,
        application_details: dict,
        analysis: str
    ):

        return self.planner_service.create_plan(
            project_structure,
            application_details,
            analysis
        )