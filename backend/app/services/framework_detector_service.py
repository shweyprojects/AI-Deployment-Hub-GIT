import json
import os


class FrameworkDetectorService:

    EXCLUDED_DIRECTORIES = {
        ".git",
        "node_modules",
        "__pycache__",
        ".venv",
        "venv",
        "dist",
        "build",
    }

    def detect(self, workspace: str):

        detected_frameworks = []

        # --------------------------------------------------
        # Check Python project
        # --------------------------------------------------

        requirements_path = os.path.join(
            workspace,
            "requirements.txt"
        )

        pyproject_path = os.path.join(
            workspace,
            "pyproject.toml"
        )

        if os.path.exists(requirements_path) or os.path.exists(pyproject_path):

            requirements = ""

            if os.path.exists(requirements_path):
                with open(
                    requirements_path,
                    "r",
                    encoding="utf-8"
                ) as file:
                    requirements = file.read().lower()

            if "fastapi" in requirements:
                detected_frameworks.append("FastAPI")

            elif "flask" in requirements:
                detected_frameworks.append("Flask")

            elif "django" in requirements:
                detected_frameworks.append("Django")

            else:
                detected_frameworks.append("Python")

        # --------------------------------------------------
        # Check Node.js / JavaScript project
        # --------------------------------------------------

        package_path = os.path.join(
            workspace,
            "package.json"
        )

        if os.path.exists(package_path):

            with open(
                package_path,
                "r",
                encoding="utf-8"
            ) as file:
                package_data = json.load(file)

            dependencies = {}

            dependencies.update(
                package_data.get("dependencies", {})
            )

            dependencies.update(
                package_data.get("devDependencies", {})
            )

            dependency_names = {
                name.lower()
                for name in dependencies.keys()
            }

            if "next" in dependency_names:
                detected_frameworks.append("Next.js")

            elif "react" in dependency_names:
                detected_frameworks.append("React")

            elif "vue" in dependency_names:
                detected_frameworks.append("Vue")

            elif "express" in dependency_names:
                detected_frameworks.append("Express")

            else:
                detected_frameworks.append("Node.js")

        # --------------------------------------------------
        # Remove duplicates
        # --------------------------------------------------

        detected_frameworks = list(
            dict.fromkeys(detected_frameworks)
        )

        return {
            "frameworks": detected_frameworks
        }