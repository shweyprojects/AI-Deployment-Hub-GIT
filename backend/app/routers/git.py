from fastapi import APIRouter

from app.schemas.git import GitCloneRequest

from app.agents.git_clone_agent import GitCloneAgent
from app.agents.project_scanner_agent import ProjectScannerAgent
from app.agents.framework_detector_agent import FrameworkDetectorAgent
from app.agents.application_detector_agent import ApplicationDetectorAgent
from app.agents.analyzer_agent import AnalyzerAgent
from app.agents.deployment_planner_agent import DeploymentPlannerAgent
from app.agents.docker_generator_agent import DockerGeneratorAgent
from app.agents.validator_agent import ValidatorAgent
from app.agents.docker_build_agent import DockerBuildAgent
from app.agents.docker_run_agent import DockerRunAgent
from app.agents.health_check_agent import HealthCheckAgent
from app.agents.recovery_agent import RecoveryAgent
from app.agents.deployment_agent import DeploymentAgent


router = APIRouter(
    prefix="/api/git",
    tags=["Git"]
)


clone_agent = GitCloneAgent()
scanner_agent = ProjectScannerAgent()
framework_agent = FrameworkDetectorAgent()
application_agent = ApplicationDetectorAgent()
analyzer_agent = AnalyzerAgent()
deployment_planner_agent = DeploymentPlannerAgent()
docker_generator_agent = DockerGeneratorAgent()
validator_agent = ValidatorAgent()
docker_build_agent = DockerBuildAgent()
docker_run_agent = DockerRunAgent()
health_check_agent = HealthCheckAgent()
recovery_agent = RecoveryAgent()
deployment_agent = DeploymentAgent()


@router.post("/clone")
def clone_repository(request: GitCloneRequest):
    return clone_agent.execute(
        str(request.repository_url)
    )


@router.post("/scan/{project_id}")
def scan_project(project_id: str):
    workspace = f"workspaces/{project_id}"

    return scanner_agent.execute(
        workspace
    )


@router.post("/detect-framework/{project_id}")
def detect_framework(project_id: str):
    workspace = f"workspaces/{project_id}"

    return framework_agent.execute(
        workspace
    )


@router.post("/detect-application/{project_id}")
def detect_application(project_id: str):
    workspace = f"workspaces/{project_id}"

    return application_agent.execute(
        workspace
    )


@router.post("/analyze/{project_id}")
def analyze_project(project_id: str):
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


@router.post("/create-deployment-plan/{project_id}")
def create_deployment_plan(project_id: str):
    workspace = f"workspaces/{project_id}"

    project_structure = scanner_agent.execute(
        workspace
    )

    application_details = application_agent.execute(
        workspace
    )

    analysis_result = analyzer_agent.execute(
        project_structure,
        application_details
    )

    analysis = analysis_result.get(
        "analysis",
        ""
    )

    return deployment_planner_agent.execute(
        project_structure,
        application_details,
        analysis
    )


@router.post("/generate-docker/{project_id}")
def generate_docker(project_id: str):
    workspace = f"workspaces/{project_id}"

    project_structure = scanner_agent.execute(
        workspace
    )

    application_details = application_agent.execute(
        workspace
    )

    analysis_result = analyzer_agent.execute(
        project_structure,
        application_details
    )

    analysis = analysis_result.get(
        "analysis",
        ""
    )

    deployment_plan = deployment_planner_agent.execute(
        project_structure,
        application_details,
        analysis
    )

    return docker_generator_agent.generate(
        workspace,
        deployment_plan
    )


@router.post("/validate/{project_id}")
def validate_deployment(project_id: str):
    workspace = f"workspaces/{project_id}"

    project_structure = scanner_agent.execute(
        workspace
    )

    application_details = application_agent.execute(
        workspace
    )

    analysis_result = analyzer_agent.execute(
        project_structure,
        application_details
    )

    analysis = analysis_result.get(
        "analysis",
        ""
    )

    deployment_plan = deployment_planner_agent.execute(
        project_structure,
        application_details,
        analysis
    )

    docker_generator_agent.generate(
        workspace,
        deployment_plan
    )

    return validator_agent.validate(
        workspace,
        deployment_plan
    )


@router.post("/build-docker/{project_id}")
def build_docker(project_id: str):
    workspace = f"workspaces/{project_id}"

    image_name = (
        f"agentic-deployment-{project_id}:latest"
    )

    result = docker_build_agent.build(
        project_path=workspace,
        image_name=image_name,
    )

    return result


@router.post("/run-docker/{project_id}")
def run_docker(project_id: str):
    workspace = f"workspaces/{project_id}"

    image_name = (
        f"agentic-deployment-{project_id}:latest"
    )

    container_name = (
        f"agentic-deployment-{project_id}"
    )

    project_structure = scanner_agent.execute(
        workspace
    )

    application_details = application_agent.execute(
        workspace
    )

    analysis_result = analyzer_agent.execute(
        project_structure,
        application_details
    )

    analysis = analysis_result.get(
        "analysis",
        ""
    )

    deployment_plan = deployment_planner_agent.execute(
        project_structure,
        application_details,
        analysis
    )

    service = deployment_plan.get(
        "services",
        [{}]
    )[0]

    port = service.get(
        "port",
        5000
    )

    return docker_run_agent.run(
        image_name=image_name,
        container_name=container_name,
        port=port,
    )


@router.post("/health-check/{project_id}")
def health_check(project_id: str):
    workspace = f"workspaces/{project_id}"

    project_structure = scanner_agent.execute(
        workspace
    )

    application_details = application_agent.execute(
        workspace
    )

    analysis_result = analyzer_agent.execute(
        project_structure,
        application_details
    )

    analysis = analysis_result.get(
        "analysis",
        ""
    )

    deployment_plan = deployment_planner_agent.execute(
        project_structure,
        application_details,
        analysis
    )

    health_check_config = deployment_plan.get(
        "health_check",
        {}
    )

    port = health_check_config.get(
        "port",
        5000
    )

    path = health_check_config.get(
        "path",
        "/"
    )

    url = f"http://localhost:{port}{path}"

    return health_check_agent.check(
        url=url
    )


@router.post("/deploy/{project_id}")
def deploy(
    project_id: str,
    request: GitCloneRequest
):
    """
    Deploy locally using Docker.
    """

    return deployment_agent.deploy(
        repo_url=str(request.repository_url),
        project_id=project_id,
    )


@router.post("/deploy-to-render/{project_id}")
def deploy_to_render(
    project_id: str,
    request: GitCloneRequest
):
    """
    Deploy the application to Render.
    """

    return deployment_agent.deploy_to_render(
        repo_url=str(request.repository_url),
        project_id=project_id,
    )