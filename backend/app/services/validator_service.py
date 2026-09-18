from pathlib import Path
from typing import Dict, Any


class ValidatorService:
    """
    Validates generated Docker deployment artifacts.
    """

    def validate(
        self,
        project_path: str,
        deployment_plan: Dict[str, Any],
    ) -> Dict[str, Any]:

        project_dir = Path(project_path)

        if not project_dir.exists():
            raise FileNotFoundError(
                f"Project path does not exist: {project_path}"
            )

        dockerfile = project_dir / "Dockerfile"
        dockerignore = project_dir / ".dockerignore"

        errors = []
        warnings = []

        # -----------------------------
        # Dockerfile validation
        # -----------------------------

        if not dockerfile.exists():
            errors.append("Dockerfile was not found.")
        else:
            dockerfile_content = dockerfile.read_text(
                encoding="utf-8"
            ).strip()

            if not dockerfile_content:
                errors.append("Dockerfile is empty.")

            if "FROM " not in dockerfile_content:
                errors.append(
                    "Dockerfile does not contain a FROM instruction."
                )

            service = (
                deployment_plan.get("services", [{}])[0]
            )

            expected_port = service.get("port")

            if expected_port:
                if f"EXPOSE {expected_port}" not in dockerfile_content:
                    warnings.append(
                        f"Dockerfile does not explicitly expose "
                        f"port {expected_port}."
                    )

            start_command = service.get("start_command")

            if start_command:
                command_parts = start_command.split()

                if not all(
                    part in dockerfile_content
                    for part in command_parts
                ):
                    warnings.append(
                        "Dockerfile may not contain the expected "
                        f"start command: {start_command}"
                    )

        # -----------------------------
        # .dockerignore validation
        # -----------------------------

        if not dockerignore.exists():
            warnings.append(
                ".dockerignore was not found."
            )

        # -----------------------------
        # Requirements validation
        # -----------------------------

        requirements_file = project_dir / "requirements.txt"

        framework = deployment_plan.get(
            "framework",
            ""
        ).lower()

        if framework == "flask":
            if not requirements_file.exists():
                errors.append(
                    "requirements.txt was not found for Flask application."
                )
            else:
                requirements_content = requirements_file.read_text(
                    encoding="utf-8"
                ).lower()

                if "flask" not in requirements_content:
                    warnings.append(
                        "Flask was detected but Flask was not found "
                        "in requirements.txt."
                    )

        # -----------------------------
        # Result
        # -----------------------------

        is_valid = len(errors) == 0

        return {
            "status": "success" if is_valid else "failed",
            "valid": is_valid,
            "project_path": str(project_dir),
            "errors": errors,
            "warnings": warnings,
            "validated_files": [
                str(dockerfile),
                str(dockerignore),
            ],
        }