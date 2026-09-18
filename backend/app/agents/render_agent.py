from typing import Any, Dict, Optional

from app.services.render_service import RenderDeploymentService


class RenderDeploymentAgent:
    """
    Agent responsible for orchestrating Docker image deployment
    through Render.
    """

    def __init__(self):
        self.service = RenderDeploymentService()

    def deploy(
        self,
        image_path: str,
        service_name: str,
        plan: str = "free",
        region: str = "singapore",
        health_check_path: str = "/",
        owner_id: Optional[str] = None,
        registry_credential_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a Render service using a Docker image.
        """

        if not image_path:
            raise ValueError(
                "Docker image path is required."
            )

        if not service_name:
            raise ValueError(
                "Render service name is required."
            )

        return self.service.create_image_service(
            service_name=service_name,
            image_path=image_path,
            owner_id=owner_id,
            registry_credential_id=registry_credential_id,
            plan=plan,
            region=region,
            health_check_path=health_check_path,
        )

    def create_registry_credential(
        self,
        owner_id: str,
    ) -> Dict[str, Any]:
        """
        Register Docker Hub credentials with Render.
        """

        if not owner_id:
            raise ValueError(
                "Render owner ID is required."
            )

        return self.service.create_registry_credential(
            owner_id=owner_id
        )

    def deploy_existing_image(
        self,
        service_id: str,
        image_url: str,
    ) -> Dict[str, Any]:
        """
        Deploy a new Docker image to an existing Render service.
        """

        if not service_id:
            raise ValueError(
                "Render service ID is required."
            )

        if not image_url:
            raise ValueError(
                "Docker image URL is required."
            )

        return self.service.deploy_image(
            service_id=service_id,
            image_url=image_url,
        )

    def get_service(
        self,
        service_id: str,
    ) -> Dict[str, Any]:
        """
        Get the current Render service details.
        """

        if not service_id:
            raise ValueError(
                "Render service ID is required."
            )

        return self.service.get_service(
            service_id
        )