import json
import os


class ApplicationDetectorService:

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

        result = []

        # --------------------------------------------------
        # Detect Python application
        # --------------------------------------------------

        requirements_path = os.path.join(
            workspace,
            "requirements.txt"
        )

        if os.path.exists(requirements_path):

            with open(
                requirements_path,
                "r",
                encoding="utf-8"
            ) as file:
                requirements = file.read().lower()

            framework = None

            if "fastapi" in requirements:
                framework = "FastAPI"

            elif "flask" in requirements:
                framework = "Flask"

            elif "django" in requirements:
                framework = "Django"

            if framework:

                entry_point = self._find_python_entry_point(
                    workspace,
                    framework
                )

                port = self._detect_python_port(
                    workspace,
                    entry_point,
                    framework
                )

                start_command = self._get_python_start_command(
                    framework,
                    entry_point
                )

                result.append({
                    "framework": framework,
                    "language": "Python",
                    "entry_point": entry_point,
                    "start_command": start_command,
                    "port": port,
                    "dependency_file": "requirements.txt"
                })

        # --------------------------------------------------
        # Detect Node.js / JavaScript application
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

            framework = "Node.js"

            if "next" in dependency_names:
                framework = "Next.js"

            elif "react" in dependency_names:
                framework = "React"

            elif "vue" in dependency_names:
                framework = "Vue"

            elif "express" in dependency_names:
                framework = "Express"

            entry_point = self._find_node_entry_point(
                workspace,
                package_data
            )

            start_command = self._get_node_start_command(
                package_data
            )

            port = self._get_node_port(
                package_data,
                framework
            )

            result.append({
                "framework": framework,
                "language": "JavaScript",
                "entry_point": entry_point,
                "start_command": start_command,
                "port": port,
                "dependency_file": "package.json"
            })

        # --------------------------------------------------
        # Return result
        # --------------------------------------------------

        return {
            "applications": result
        }

    # ======================================================
    # Python helpers
    # ======================================================

    def _find_python_entry_point(
        self,
        workspace: str,
        framework: str
    ):

        preferred_files = []

        if framework == "Flask":
            preferred_files = [
                "app.py",
                "main.py",
                "application.py"
            ]

        elif framework == "FastAPI":
            preferred_files = [
                "main.py",
                "app.py"
            ]

        elif framework == "Django":
            preferred_files = [
                "manage.py"
            ]

        for filename in preferred_files:

            path = os.path.join(
                workspace,
                filename
            )

            if os.path.exists(path):
                return filename

        # Search Python files if preferred file
        # was not found
        for root, dirs, files in os.walk(workspace):

            dirs[:] = [
                directory
                for directory in dirs
                if directory not in self.EXCLUDED_DIRECTORIES
            ]

            for filename in files:

                if filename.endswith(".py"):
                    return os.path.relpath(
                        os.path.join(root, filename),
                        workspace
                    )

        return None

    def _detect_python_port(
        self,
        workspace: str,
        entry_point: str,
        framework: str
    ):

        if not entry_point:
            return self._default_python_port(framework)

        entry_path = os.path.join(
            workspace,
            entry_point
        )

        if not os.path.exists(entry_path):
            return self._default_python_port(framework)

        try:

            with open(
                entry_path,
                "r",
                encoding="utf-8"
            ) as file:
                content = file.read()

            # Simple detection for common Flask pattern
            # app.run(port=5000)
            if "port=" in content:

                import re

                match = re.search(
                    r"port\s*=\s*(\d+)",
                    content
                )

                if match:
                    return int(match.group(1))

        except Exception:
            pass

        return self._default_python_port(framework)

    def _default_python_port(self, framework: str):

        if framework == "Flask":
            return 5000

        if framework == "FastAPI":
            return 8000

        if framework == "Django":
            return 8000

        return 8000

    def _get_python_start_command(
        self,
        framework: str,
        entry_point: str
    ):

        if not entry_point:
            return None

        if framework == "Flask":
            return f"python {entry_point}"

        if framework == "FastAPI":

            module = entry_point.replace(
                ".py",
                ""
            ).replace(
                "/",
                "."
            ).replace(
                "\\",
                "."
            )

            return f"uvicorn {module}:app --host 0.0.0.0 --port 8000"

        if framework == "Django":
            return "python manage.py runserver 0.0.0.0:8000"

        return f"python {entry_point}"

    # ======================================================
    # Node.js helpers
    # ======================================================

    def _find_node_entry_point(
        self,
        workspace: str,
        package_data: dict
    ):

        # Check package.json "main"
        main_file = package_data.get("main")

        if main_file:

            main_path = os.path.join(
                workspace,
                main_file
            )

            if os.path.exists(main_path):
                return main_file

        # Common Node.js entry files
        preferred_files = [
            "server.js",
            "index.js",
            "app.js",
            "main.js"
        ]

        for filename in preferred_files:

            path = os.path.join(
                workspace,
                filename
            )

            if os.path.exists(path):
                return filename

        return None

    def _get_node_start_command(
        self,
        package_data: dict
    ):

        scripts = package_data.get(
            "scripts",
            {}
        )

        if "start" in scripts:
            return "npm start"

        if "dev" in scripts:
            return "npm run dev"

        if "serve" in scripts:
            return "npm run serve"

        return None

    def _get_node_port(
        self,
        package_data: dict,
        framework: str
    ):

        scripts = package_data.get(
            "scripts",
            {}
        )

        start_script = scripts.get(
            "start",
            ""
        ).lower()

        # Common port values in scripts
        import re

        match = re.search(
            r"(?:port[=\s:]*)?(\d{4})",
            start_script
        )

        if match:
            return int(match.group(1))

        if framework == "Next.js":
            return 3000

        if framework == "React":
            return 3000

        if framework == "Vue":
            return 5173

        if framework == "Express":
            return 3000

        return 3000