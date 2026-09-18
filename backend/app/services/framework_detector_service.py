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

        if not os.path.exists(workspace):
            return {
                "error": "Workspace not found",
                "workspace": workspace,
                "frameworks": []
            }

        detected_frameworks = []
        dependency_files = []

        # --------------------------------------------------
        # Find dependency files anywhere in the project
        # --------------------------------------------------

        for root, dirs, files in os.walk(workspace):

            dirs[:] = [
                directory
                for directory in dirs
                if directory not in self.EXCLUDED_DIRECTORIES
            ]

            for filename in files:

                if filename in {
                    "requirements.txt",
                    "pyproject.toml",
                    "package.json"
                }:
                    dependency_files.append(
                        os.path.join(root, filename)
                    )

        # --------------------------------------------------
        # Analyze dependency files
        # --------------------------------------------------

        for dependency_file in dependency_files:

            filename = os.path.basename(
                dependency_file
            ).lower()

            # ----------------------------------------------
            # Python requirements.txt
            # ----------------------------------------------

            if filename == "requirements.txt":

                try:

                    with open(
                        dependency_file,
                        "r",
                        encoding="utf-8"
                    ) as file:
                        content = file.read().lower()

                    if "fastapi" in content:
                        detected_frameworks.append(
                            "FastAPI"
                        )

                    if "flask" in content:
                        detected_frameworks.append(
                            "Flask"
                        )

                    if "django" in content:
                        detected_frameworks.append(
                            "Django"
                        )

                    if (
                        "fastapi" not in content
                        and
                        "flask" not in content
                        and
                        "django" not in content
                    ):
                        detected_frameworks.append(
                            "Python"
                        )

                except Exception:
                    pass

            # ----------------------------------------------
            # Python pyproject.toml
            # ----------------------------------------------

            elif filename == "pyproject.toml":

                try:

                    with open(
                        dependency_file,
                        "r",
                        encoding="utf-8"
                    ) as file:
                        content = file.read().lower()

                    if "fastapi" in content:
                        detected_frameworks.append(
                            "FastAPI"
                        )

                    if "flask" in content:
                        detected_frameworks.append(
                            "Flask"
                        )

                    if "django" in content:
                        detected_frameworks.append(
                            "Django"
                        )

                    if (
                        "fastapi" not in content
                        and
                        "flask" not in content
                        and
                        "django" not in content
                    ):
                        detected_frameworks.append(
                            "Python"
                        )

                except Exception:
                    pass

            # ----------------------------------------------
            # Node.js package.json
            # ----------------------------------------------

            elif filename == "package.json":

                try:

                    with open(
                        dependency_file,
                        "r",
                        encoding="utf-8"
                    ) as file:
                        package_data = json.load(file)

                    dependencies = {}

                    dependencies.update(
                        package_data.get(
                            "dependencies",
                            {}
                        )
                    )

                    dependencies.update(
                        package_data.get(
                            "devDependencies",
                            {}
                        )
                    )

                    dependency_names = {
                        name.lower()
                        for name in dependencies.keys()
                    }

                    if "next" in dependency_names:
                        detected_frameworks.append(
                            "Next.js"
                        )

                    elif "react" in dependency_names:
                        detected_frameworks.append(
                            "React"
                        )

                    elif "vue" in dependency_names:
                        detected_frameworks.append(
                            "Vue"
                        )

                    elif "express" in dependency_names:
                        detected_frameworks.append(
                            "Express"
                        )

                    else:
                        detected_frameworks.append(
                            "Node.js"
                        )

                except Exception:
                    pass

        # --------------------------------------------------
        # Remove duplicates
        # --------------------------------------------------

        detected_frameworks = list(
            dict.fromkeys(detected_frameworks)
        )

        # --------------------------------------------------
        # Return result
        # --------------------------------------------------

        return {
            "frameworks": detected_frameworks,
            "dependency_files": [
                os.path.relpath(
                    path,
                    workspace
                )
                for path in dependency_files
            ]
        }