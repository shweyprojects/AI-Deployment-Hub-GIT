import os
from typing import Any, Dict, Optional

import requests


class RenderDeploymentService:
    """
    Service responsible for deploying Docker images to Render.
    """

    BASE_URL = "https://api.render.com/v1"
    REGISTRY_CREDENTIAL_NAME = "agentic-deployment-dockerhub"

    def __init__(self):
        self.api_key = os.getenv("RENDER_API_KEY")

        if not self.api_key:
            raise RuntimeError(
                "RENDER_API_KEY is not configured."
            )

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    # =========================================================
    # WORKSPACE
    # =========================================================

    def get_workspaces(self) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/owners",
            headers=self.headers,
            params={"limit": 100},
            timeout=30,
        )

        if response.status_code >= 400:
            return {
                "status": "failed",
                "status_code": response.status_code,
                "error": response.text,
            }

        return {
            "status": "success",
            "workspaces": response.json(),
        }

    def get_first_workspace_id(self) -> str:
        result = self.get_workspaces()

        if result["status"] != "success":
            raise RuntimeError(
                "Unable to retrieve Render workspaces: "
                f"{result.get('error', 'Unknown error')}"
            )

        workspaces = result.get("workspaces", [])

        if not workspaces:
            raise RuntimeError(
                "No Render workspaces were found."
            )

        first_workspace = workspaces[0]

        workspace = first_workspace.get(
            "owner",
            first_workspace,
        )

        workspace_id = workspace.get("id")

        if not workspace_id:
            raise RuntimeError(
                "Render workspace ID was not found."
            )

        return workspace_id

    # =========================================================
    # REGISTRY CREDENTIALS
    # =========================================================

    def get_registry_credentials(
        self,
        owner_id: str,
    ) -> Dict[str, Any]:
        """
        Find existing Docker registry credentials.
        """

        if not owner_id:
            raise ValueError(
                "Render owner ID is required."
            )

        username = os.getenv(
            "DOCKER_USERNAME"
        )

        params = {
            "ownerId": [owner_id],
            "type": ["DOCKER"],
            "name": [
                self.REGISTRY_CREDENTIAL_NAME
            ],
            "limit": 100,
        }

        if username:
            params["username"] = [username]

        response = requests.get(
            f"{self.BASE_URL}/registrycredentials",
            headers=self.headers,
            params=params,
            timeout=30,
        )

        if response.status_code >= 400:
            return {
                "status": "failed",
                "status_code": response.status_code,
                "error": response.text,
            }

        return {
            "status": "success",
            "credentials": response.json(),
        }

    def create_registry_credential(
        self,
        owner_id: str,
    ) -> Dict[str, Any]:
        """
        Reuse an existing Docker Hub credential when
        available. Otherwise create a new credential.
        """

        if not owner_id:
            raise ValueError(
                "Render owner ID is required."
            )

        # -----------------------------------------------------
        # Check existing credential
        # -----------------------------------------------------

        existing_result = (
            self.get_registry_credentials(
                owner_id=owner_id
            )
        )

        if existing_result["status"] == "success":

            credentials = existing_result.get(
                "credentials",
                [],
            )

            if isinstance(
                credentials,
                dict,
            ):
                credentials = credentials.get(
                    "items",
                    credentials.get(
                        "credentials",
                        [],
                    ),
                )

            if isinstance(
                credentials,
                list,
            ):

                for item in credentials:

                    credential = item.get(
                        "credential",
                        item,
                    )

                    credential_id = credential.get(
                        "id"
                    )

                    if credential_id:
                        return {
                            "status": "success",
                            "credential": credential,
                            "credential_id": (
                                credential_id
                            ),
                            "reused": True,
                        }

        # -----------------------------------------------------
        # Create credential
        # -----------------------------------------------------

        username = os.getenv(
            "DOCKER_USERNAME"
        )

        access_token = os.getenv(
            "DOCKER_ACCESS_TOKEN"
        )

        if not username:
            raise RuntimeError(
                "DOCKER_USERNAME is not configured."
            )

        if not access_token:
            raise RuntimeError(
                "DOCKER_ACCESS_TOKEN is not configured."
            )

        payload = {
            "registry": "DOCKER",
            "name": self.REGISTRY_CREDENTIAL_NAME,
            "username": username,
            "authToken": access_token,
            "ownerId": owner_id,
        }

        response = requests.post(
            f"{self.BASE_URL}/registrycredentials",
            headers=self.headers,
            json=payload,
            timeout=30,
        )

        if response.status_code >= 400:
            return {
                "status": "failed",
                "status_code": response.status_code,
                "error": response.text,
            }

        data = response.json()

        return {
            "status": "success",
            "credential": data,
            "credential_id": data.get("id"),
            "reused": False,
        }

    # =========================================================
    # CREATE IMAGE-BACKED SERVICE
    # =========================================================

    def create_image_service(
        self,
        service_name: str,
        image_path: str,
        owner_id: Optional[str] = None,
        registry_credential_id: Optional[str] = None,
        plan: str = "free",
        region: str = "singapore",
        health_check_path: str = "/",
    ) -> Dict[str, Any]:
        """
        Create a Render web service backed by an existing
        Docker image.
        """

        if not service_name:
            raise ValueError(
                "Render service name is required."
            )

        if not image_path:
            raise ValueError(
                "Docker image path is required."
            )

        if not owner_id:
            owner_id = (
                self.get_first_workspace_id()
            )

        # -----------------------------------------------------
        # Image configuration
        # -----------------------------------------------------

        image_config = {
            "ownerId": owner_id,
            "imagePath": image_path,
        }

        if registry_credential_id:
            image_config[
                "registryCredentialId"
            ] = registry_credential_id

        # -----------------------------------------------------
        # Render service payload
        #
        # IMPORTANT:
        # This is an existing-image deployment.
        #
        # runtime MUST be "image".
        # -----------------------------------------------------

        payload = {
            "type": "web_service",
            "name": service_name,
            "ownerId": owner_id,
            "image": image_config,
            "serviceDetails": {
                "runtime": "image",
                "plan": plan,
                "region": region,
                "healthCheckPath": health_check_path,
            },
        }

        response = requests.post(
            f"{self.BASE_URL}/services",
            headers=self.headers,
            json=payload,
            timeout=30,
        )

        if response.status_code >= 400:
            return {
                "status": "failed",
                "status_code": response.status_code,
                "error": response.text,
                "request_payload": {
                    "type": payload.get(
                        "type"
                    ),
                    "name": payload.get(
                        "name"
                    ),
                    "ownerId": payload.get(
                        "ownerId"
                    ),
                    "image": {
                        "ownerId": image_config.get(
                            "ownerId"
                        ),
                        "imagePath": image_config.get(
                            "imagePath"
                        ),
                        "registryCredentialId": (
                            image_config.get(
                                "registryCredentialId"
                            )
                        ),
                    },
                    "serviceDetails": {
                        "runtime": "image",
                        "plan": plan,
                        "region": region,
                        "healthCheckPath": (
                            health_check_path
                        ),
                    },
                },
            }

        data = response.json()

        service = data.get(
            "service",
            data,
        )

        # -----------------------------------------------------
        # Extract URL
        # -----------------------------------------------------

        service_url = service.get(
            "url"
        )

        if not service_url:

            service_details = service.get(
                "serviceDetails",
                {},
            )

            service_url = service_details.get(
                "url"
            )

        return {
            "status": "success",
            "service_id": service.get(
                "id"
            ),
            "service_name": service.get(
                "name"
            ),
            "service_url": service_url,
            "owner_id": service.get(
                "ownerId"
            ),
            "plan": service.get(
                "plan"
            ),
            "region": service.get(
                "region"
            ),
            "health_check_path": service.get(
                "healthCheckPath"
            ),
            "raw_response": data,
        }

    # =========================================================
    # DEPLOY IMAGE
    # =========================================================

    def deploy_image(
        self,
        service_id: str,
        image_url: str,
    ) -> Dict[str, Any]:
        """
        Trigger a deployment of a new image to an
        existing Render image-backed service.
        """

        if not service_id:
            raise ValueError(
                "Render service ID is required."
            )

        if not image_url:
            raise ValueError(
                "Image URL is required."
            )

        payload = {
            "imageUrl": image_url,
            "deployMode": "deploy_only",
        }

        response = requests.post(
            f"{self.BASE_URL}/services/"
            f"{service_id}/deploys",
            headers=self.headers,
            json=payload,
            timeout=30,
        )

        if response.status_code >= 400:
            return {
                "status": "failed",
                "status_code": response.status_code,
                "error": response.text,
            }

        return {
            "status": "success",
            "service_id": service_id,
            "image_url": image_url,
            "deployment": response.json(),
        }

    # =========================================================
    # GET SERVICE
    # =========================================================

    def get_service(
        self,
        service_id: str,
    ) -> Dict[str, Any]:
        """
        Retrieve a Render service.
        """

        if not service_id:
            raise ValueError(
                "Render service ID is required."
            )

        response = requests.get(
            f"{self.BASE_URL}/services/{service_id}",
            headers=self.headers,
            timeout=30,
        )

        if response.status_code >= 400:
            return {
                "status": "failed",
                "status_code": response.status_code,
                "error": response.text,
            }

        return {
            "status": "success",
            "service": response.json(),
        }