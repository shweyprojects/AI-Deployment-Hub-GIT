from app.services.application_detector_service import (
    ApplicationDetectorService
)


class ApplicationDetectorAgent:

    def __init__(self):
        self.detector_service = ApplicationDetectorService()

    def execute(self, workspace: str):

        return self.detector_service.detect(
            workspace
        )