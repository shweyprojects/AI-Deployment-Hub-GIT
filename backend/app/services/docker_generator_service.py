from pathlib import Path
from typing import Dict, Any


class DockerGeneratorService:
    """
    Generates Docker deployment artifacts based on the deployment plan.
    """

    def generate(
        self,
        project_path: str,
        deployment_plan: Dict[str, Any],
    ) -> Dict[str, Any]:
        project_dir = Path(project_path)

        if not project_dir.exists():
            raise FileNotFoundError(
                f"Project path does not exist: {project_path}"
            )

        services = deployment_plan.get("services", [])

        if not services:
            raise ValueError(
                "Deployment plan does not contain any services."
            )

        service = services[0]

        port = service.get("port", 5000)
        start_command = service.get(
            "start_command",
            "python app.py"
        )

        dockerfile_content = self._generate_dockerfile(
            port=port,
            start_command=start_command
        )

        dockerignore_content = self._generate_dockerignore()

        dockerfile_path = project_dir / "Dockerfile"
        dockerignore_path = project_dir / ".dockerignore"

        dockerfile_path.write_text(
            dockerfile_content,
            encoding="utf-8"
        )

        dockerignore_path.write_text(
            dockerignore_content,
            encoding="utf-8"
        )

        return {
            "status": "success",
            "project_path": str(project_dir),
            "files": [
                {
                    "name": "Dockerfile",
                    "path": str(dockerfile_path),
                    "content": dockerfile_content
                },
                {
                    "name": ".dockerignore",
                    "path": str(dockerignore_path),
                    "content": dockerignore_content
                }
            ]
        }

    def _generate_dockerfile(
        self,
        port: int,
        start_command: str
    ) -> str:
        command_parts = start_command.split()

        command_json = ", ".join(
            f'"{part}"'
            for part in command_parts
        )

        return f"""FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE {port}

CMD [{command_json}]
"""

    def _generate_dockerignore(self) -> str:
        return """__pycache__
*.pyc
*.pyo
*.pyd
.Python
.venv
venv
.env
.git
.gitignore
.vscode
.idea
node_modules
dist
build
"""