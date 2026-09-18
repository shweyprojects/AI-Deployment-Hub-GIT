import subprocess
from typing import Dict, Any


class DockerRunService:
    """
    Runs a Docker container for the application.
    """

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

        # Remove an existing container with the same name.
        remove_command = [
            "docker",
            "rm",
            "-f",
            container_name,
        ]

        try:
            subprocess.run(
                remove_command,
                capture_output=True,
                text=True,
                check=False,
            )

            command = [
                "docker",
                "run",
                "-d",
                "--name",
                container_name,
                "-p",
                str(port),
                image_name,
            ]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
            )

        except FileNotFoundError:
            raise RuntimeError(
                "Docker was not found. "
                "Make sure Docker Desktop is installed and running."
            )

        if result.returncode != 0:
            return {
                "status": "failed",
                "image_name": image_name,
                "container_name": container_name,
                "port": port,
                "error": result.stderr,
                "output": result.stdout,
            }

        container_id = result.stdout.strip()

        port_result = subprocess.run(
            ["docker", "port", container_name, f"{port}/tcp"],
            capture_output=True,
            text=True,
            check=False,
        )

        if port_result.returncode != 0 or not port_result.stdout.strip():
            return {
                "status": "failed",
                "image_name": image_name,
                "container_name": container_name,
                "container_id": container_id,
                "port": port,
                "error": "Container started, but its host port could not be determined.",
                "output": port_result.stderr,
            }

        host_port = port_result.stdout.strip().splitlines()[0].rsplit(":", 1)[-1]

        return {
            "status": "success",
            "image_name": image_name,
            "container_name": container_name,
            "container_id": container_id,
            "port": int(host_port),
            "container_port": port,
            "url": f"http://localhost:{host_port}",
        }
