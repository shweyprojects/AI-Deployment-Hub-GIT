import os


class ProjectScannerService:

    EXCLUDED_DIRECTORIES = {
        ".git",
        "node_modules",
        "__pycache__",
        ".venv",
        "venv",
        "dist",
        "build"
    }

    def scan(self, workspace: str):

        files = []
        folders = []

        for root, dirs, filenames in os.walk(workspace):

            # Remove excluded directories from scanning
            dirs[:] = [
                directory
                for directory in dirs
                if directory not in self.EXCLUDED_DIRECTORIES
            ]

            for folder in dirs:
                folders.append(
                    os.path.relpath(
                        os.path.join(root, folder),
                        workspace
                    )
                )

            for filename in filenames:
                files.append(
                    os.path.relpath(
                        os.path.join(root, filename),
                        workspace
                    )
                )

        return {
            "files": files,
            "folders": folders
        }