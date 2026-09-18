import os
import subprocess
from typing import Dict, Any


class DockerRegistryService:
    """
    Service responsible for authenticating with a Docker registry
    and pushing Docker images.
    """

    def __init__(self):
        self.registry = os.getenv(
            "DOCKER_REGISTRY",
            "docker.io"
        )

        self.username = os.getenv(
            "DOCKER_USERNAME"
        )

        self.repository = os.getenv(
            "DOCKER_REPOSITORY"
        )

        self.access_token = os.getenv(
            "DOCKER_ACCESS_TOKEN"
        )

    def _validate_configuration(self):
        if not self.username:
            raise RuntimeError(
                "DOCKER_USERNAME is not configured."
            )

        if not self.repository:
            raise RuntimeError(
                "DOCKER_REPOSITORY is not configured."
            )

        if not self.access_token:
            raise RuntimeError(
                "DOCKER_ACCESS_TOKEN is not configured."
            )

    def login(self) -> Dict[str, Any]:
        """
        Authenticate Docker CLI with the configured registry.
        """

        self._validate_configuration()

        try:
            result = subprocess.run(
                [
                    "docker",
                    "login",
                    self.registry,
                    "--username",
                    self.username,
                    "--password-stdin",
                ],
                input=self.access_token,
                capture_output=True,
                text=True,
                check=False,
            )

        except FileNotFoundError:
            raise RuntimeError(
                "Docker was not found. "
                "Make sure Docker Desktop is installed "
                "and running."
            )

        if result.returncode != 0:
            return {
                "status": "failed",
                "stage": "docker_login",
                "error": result.stderr,
            }

        return {
            "status": "success",
            "stage": "docker_login",
            "registry": self.registry,
            "username": self.username,
        }

    def push_image(
        self,
        local_image: str,
        tag: str,
    ) -> Dict[str, Any]:
        """
        Tag and push a local Docker image to Docker Hub.
        """

        self._validate_configuration()

        if not local_image:
            raise ValueError(
                "Local Docker image name is required."
            )

        if not tag:
            raise ValueError(
                "Docker image tag is required."
            )

        remote_image = (
            f"{self.registry}/"
            f"{self.username}/"
            f"{self.repository}:"
            f"{tag}"
        )

        login_result = self.login()

        if login_result.get("status") != "success":
            return login_result

        try:
            tag_result = subprocess.run(
                [
                    "docker",
                    "tag",
                    local_image,
                    remote_image,
                ],
                capture_output=True,
                text=True,
                check=False,
            )

        except FileNotFoundError:
            raise RuntimeError(
                "Docker was not found."
            )

        if tag_result.returncode != 0:
            return {
                "status": "failed",
                "stage": "docker_tag",
                "error": tag_result.stderr,
                "output": tag_result.stdout,
            }

        try:
            push_result = subprocess.run(
                [
                    "docker",
                    "push",
                    remote_image,
                ],
                capture_output=True,
                text=True,
                check=False,
            )

        except FileNotFoundError:
            raise RuntimeError(
                "Docker was not found."
            )

        if push_result.returncode != 0:
            return {
                "status": "failed",
                "stage": "docker_push",
                "image": remote_image,
                "error": push_result.stderr,
                "output": push_result.stdout,
            }

        return {
            "status": "success",
            "stage": "docker_push",
            "registry": self.registry,
            "image": remote_image,
            "tag": tag,
            "output": push_result.stdout,
        }