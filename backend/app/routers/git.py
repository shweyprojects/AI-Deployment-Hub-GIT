from fastapi import APIRouter

from app.schemas.git import GitCloneRequest

from app.agents.git_clone_agent import (
    GitCloneAgent
)

from app.agents.project_scanner_agent import (
    ProjectScannerAgent
)

from app.agents.framework_detector_agent import (
    FrameworkDetectorAgent
)

from app.agents.application_detector_agent import (
    ApplicationDetectorAgent
)

from app.agents.analyzer_agent import (
    AnalyzerAgent
)


router = APIRouter(
    prefix="/api/git",
    tags=["Git"]
)


clone_agent = GitCloneAgent()

scanner_agent = ProjectScannerAgent()

framework_agent = FrameworkDetectorAgent()

application_agent = ApplicationDetectorAgent()

analyzer_agent = AnalyzerAgent()


@router.post("/clone")
def clone_repository(
    request: GitCloneRequest
):

    return clone_agent.execute(
        str(request.repository_url)
    )


@router.post("/scan/{project_id}")
def scan_project(
    project_id: str
):

    workspace = f"workspaces/{project_id}"

    return scanner_agent.execute(
        workspace
    )


@router.post("/detect-framework/{project_id}")
def detect_framework(
    project_id: str
):

    workspace = f"workspaces/{project_id}"

    return framework_agent.execute(
        workspace
    )


@router.post("/detect-application/{project_id}")
def detect_application(
    project_id: str
):

    workspace = f"workspaces/{project_id}"

    return application_agent.execute(
        workspace
    )


@router.post("/analyze/{project_id}")
def analyze_project(
    project_id: str
):

    workspace = f"workspaces/{project_id}"

    project_structure = scanner_agent.execute(
        workspace
    )

    application_details = application_agent.execute(
        workspace
    )

    return analyzer_agent.execute(
        project_structure,
        application_details
    )