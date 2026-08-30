from app.services.project_scanner_service import ProjectScannerService


class ProjectScannerAgent:

    def __init__(self):
        self.scanner_service = ProjectScannerService()

    def execute(self, workspace: str):

        return self.scanner_service.scan(workspace)