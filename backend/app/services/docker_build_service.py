import subprocess
from pathlib import Path
from typing import Dict, Any


class DockerBuildService:
    """
    Builds a Docker image for the application.
    """

    def build(
        self,
        project_path: str,
        image_name: str,
    ) -> Dict[str, Any]:

        project_dir = Path(project_path)

        if not project_dir.exists():
            raise FileNotFoundError(
                f"Project path does not exist: {project_path}"
            )

        dockerfile = project_dir / "Dockerfile"

        if not dockerfile.exists():
            raise FileNotFoundError(
                "Dockerfile was not found. "
                "Generate Docker artifacts before building."
            )

        if not image_name:
            raise ValueError("Docker image name is required.")

        command = [
            "docker",
            "build",
            "-t",
            image_name,
            str(project_dir),
        ]

        try:
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
                "error": result.stderr,
                "output": result.stdout,
            }

        return {
            "status": "success",
            "image_name": image_name,
            "output": result.stdout,
        }