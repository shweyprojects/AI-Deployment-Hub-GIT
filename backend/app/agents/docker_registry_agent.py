from typing import Dict, Any

from app.services.docker_registry_service import DockerRegistryService


class DockerRegistryAgent:
    """
    Agent responsible for orchestrating Docker image
    publishing to a container registry.
    """

    def __init__(self):
        self.service = DockerRegistryService()

    def push(
        self,
        local_image: str,
        tag: str,
    ) -> Dict[str, Any]:
        """
        Push a locally built Docker image to the registry.
        """

        if not local_image:
            raise ValueError(
                "Local Docker image name is required."
            )

        if not tag:
            raise ValueError(
                "Docker image tag is required."
            )

        return self.service.push_image(
            local_image=local_image,
            tag=tag,
        )