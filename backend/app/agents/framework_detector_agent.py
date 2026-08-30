from app.services.framework_detector_service import (
    FrameworkDetectorService
)


class FrameworkDetectorAgent:

    def __init__(self):
        self.detector_service = FrameworkDetectorService()

    def execute(self, workspace: str):

        return self.detector_service.detect(workspace)