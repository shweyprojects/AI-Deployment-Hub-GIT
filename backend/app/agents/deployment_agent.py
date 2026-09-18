from typing import Dict, Any

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
from app.agents.docker_registry_agent import DockerRegistryAgent
from app.agents.render_agent import RenderDeploymentAgent


class DeploymentAgent:
    """
    Main orchestration agent for the Agentic Deployment Hub.

    Supports:

    Local:
        clone -> scan -> analyze -> plan -> dockerize
        -> validate -> build -> run -> health check -> recovery

    Cloud:
        clone -> scan -> analyze -> plan -> dockerize
        -> validate -> build -> Docker Hub
        -> Render -> public URL
    """

    def __init__(self):
        self.git_clone_agent = GitCloneAgent()
        self.scanner_agent = ProjectScannerAgent()
        self.framework_agent = FrameworkDetectorAgent()
        self.application_agent = ApplicationDetectorAgent()
        self.analyzer_agent = AnalyzerAgent()
        self.deployment_planner_agent = DeploymentPlannerAgent()
        self.docker_generator_agent = DockerGeneratorAgent()
        self.validator_agent = ValidatorAgent()
        self.docker_build_agent = DockerBuildAgent()
        self.docker_run_agent = DockerRunAgent()
        self.health_check_agent = HealthCheckAgent()
        self.recovery_agent = RecoveryAgent()

        self.docker_registry_agent = DockerRegistryAgent()
        self.render_agent = RenderDeploymentAgent()

    # ============================================================
    # LOCAL DEPLOYMENT
    # ============================================================

    def deploy(
        self,
        repo_url: str,
        project_id: str,
    ) -> Dict[str, Any]:

        if not repo_url:
            raise ValueError("Repository URL is required.")

        if not project_id:
            raise ValueError("Project ID is required.")

        steps = []

        # ---------------------------------------------------------
        # 1. Clone
        # ---------------------------------------------------------
        clone_result = self.git_clone_agent.execute(
            repo_url,
            project_id,
        )

        steps.append({
            "step": "git_clone",
            "status": "success",
            "result": clone_result,
        })

        workspace = f"workspaces/{project_id}"

        # ---------------------------------------------------------
        # 2. Scan
        # ---------------------------------------------------------
        project_structure = self.scanner_agent.execute(
            workspace,
        )

        steps.append({
            "step": "project_scan",
            "status": "success",
            "result": project_structure,
        })

        # ---------------------------------------------------------
        # 3. Framework detection
        # ---------------------------------------------------------
        framework_result = self.framework_agent.execute(
            workspace,
        )

        steps.append({
            "step": "framework_detection",
            "status": "success",
            "result": framework_result,
        })

        # ---------------------------------------------------------
        # 4. Application detection
        # ---------------------------------------------------------
        application_details = self.application_agent.execute(
            workspace,
        )

        steps.append({
            "step": "application_detection",
            "status": "success",
            "result": application_details,
        })

        # ---------------------------------------------------------
        # 5. AI analysis
        # ---------------------------------------------------------
        analysis_result = self.analyzer_agent.execute(
            project_structure,
            application_details,
        )

        analysis = analysis_result.get(
            "analysis",
            "",
        )

        steps.append({
            "step": "ai_analysis",
            "status": "success",
            "result": analysis_result,
        })

        # ---------------------------------------------------------
        # 6. Deployment plan
        # ---------------------------------------------------------
        deployment_plan = self.deployment_planner_agent.execute(
            project_structure,
            application_details,
            analysis,
        )

        steps.append({
            "step": "deployment_plan",
            "status": "success",
            "result": deployment_plan,
        })

        # ---------------------------------------------------------
        # 7. Generate Docker artifacts
        # ---------------------------------------------------------
        docker_result = self.docker_generator_agent.generate(
            workspace,
            deployment_plan,
        )

        steps.append({
            "step": "docker_generation",
            "status": "success",
            "result": docker_result,
        })

        # ---------------------------------------------------------
        # 8. Validate
        # ---------------------------------------------------------
        validation_result = self.validator_agent.validate(
            workspace,
            deployment_plan,
        )

        steps.append({
            "step": "validation",
            "status": (
                "success"
                if validation_result.get("valid")
                else "failed"
            ),
            "result": validation_result,
        })

        if not validation_result.get("valid"):
            return {
                "status": "failed",
                "project_id": project_id,
                "stage": "validation",
                "deployment_type": "local",
                "steps": steps,
                "error": "Deployment validation failed.",
            }

        # ---------------------------------------------------------
        # 9. Build Docker image
        # ---------------------------------------------------------
        image_name = (
            f"agentic-deployment-{project_id}:latest"
        )

        build_result = self.docker_build_agent.build(
            project_path=workspace,
            image_name=image_name,
        )

        steps.append({
            "step": "docker_build",
            "status": build_result.get("status"),
            "result": build_result,
        })

        if build_result.get("status") != "success":
            return {
                "status": "failed",
                "project_id": project_id,
                "stage": "docker_build",
                "deployment_type": "local",
                "steps": steps,
                "error": "Docker image build failed.",
            }

        # ---------------------------------------------------------
        # 10. Local Docker run
        # ---------------------------------------------------------
        container_name = (
            f"agentic-deployment-{project_id}"
        )

        service = deployment_plan.get(
            "services",
            [{}],
        )[0]

        port = service.get(
            "port",
            5000,
        )

        run_result = self.docker_run_agent.run(
            image_name=image_name,
            container_name=container_name,
            port=port,
        )

        steps.append({
            "step": "docker_run",
            "status": run_result.get("status"),
            "result": run_result,
        })

        if run_result.get("status") != "success":
            return {
                "status": "failed",
                "project_id": project_id,
                "stage": "docker_run",
                "deployment_type": "local",
                "steps": steps,
                "error": "Docker container failed to start.",
            }

        # ---------------------------------------------------------
        # 11. Local health check
        # ---------------------------------------------------------
        health_check = deployment_plan.get(
            "health_check",
            {},
        )

        health_path = health_check.get(
            "path",
            "/",
        )

        health_url = (
            f"http://localhost:{port}"
            f"{health_path}"
        )

        health_result = self.health_check_agent.check(
            url=health_url,
        )

        steps.append({
            "step": "health_check",
            "status": (
                "success"
                if health_result.get("healthy")
                else "failed"
            ),
            "result": health_result,
        })

        if not health_result.get("healthy"):

            recovery_result = self.recovery_agent.recover(
                image_name=image_name,
                container_name=container_name,
                port=port,
                health_url=health_url,
            )

            steps.append({
                "step": "recovery",
                "status": recovery_result.get("status"),
                "result": recovery_result,
            })

            if not recovery_result.get("recovered"):
                return {
                    "status": "failed",
                    "project_id": project_id,
                    "stage": "recovery",
                    "deployment_type": "local",
                    "steps": steps,
                    "error": (
                        "Application failed health check "
                        "and recovery was unsuccessful."
                    ),
                }

        return {
            "status": "success",
            "project_id": project_id,
            "stage": "deployed",
            "deployment_type": "local",
            "url": health_url,
            "image_name": image_name,
            "container_name": container_name,
            "port": port,
            "steps": steps,
        }

    # ============================================================
    # RENDER CLOUD DEPLOYMENT
    # ============================================================

    def deploy_to_render(
        self,
        repo_url: str,
        project_id: str,
    ) -> Dict[str, Any]:

        if not repo_url:
            raise ValueError("Repository URL is required.")

        if not project_id:
            raise ValueError("Project ID is required.")

        steps = []

        # ---------------------------------------------------------
        # 1. Clone
        # ---------------------------------------------------------
        clone_result = self.git_clone_agent.execute(
            repo_url,
            project_id,
        )

        steps.append({
            "step": "git_clone",
            "status": "success",
            "result": clone_result,
        })

        workspace = f"workspaces/{project_id}"

        # ---------------------------------------------------------
        # 2. Scan
        # ---------------------------------------------------------
        project_structure = self.scanner_agent.execute(
            workspace,
        )

        steps.append({
            "step": "project_scan",
            "status": "success",
            "result": project_structure,
        })

        # ---------------------------------------------------------
        # 3. Framework detection
        # ---------------------------------------------------------
        framework_result = self.framework_agent.execute(
            workspace,
        )

        steps.append({
            "step": "framework_detection",
            "status": "success",
            "result": framework_result,
        })

        # ---------------------------------------------------------
        # 4. Application detection
        # ---------------------------------------------------------
        application_details = self.application_agent.execute(
            workspace,
        )

        steps.append({
            "step": "application_detection",
            "status": "success",
            "result": application_details,
        })

        # ---------------------------------------------------------
        # 5. AI analysis
        # ---------------------------------------------------------
        analysis_result = self.analyzer_agent.execute(
            project_structure,
            application_details,
        )

        analysis = analysis_result.get(
            "analysis",
            "",
        )

        steps.append({
            "step": "ai_analysis",
            "status": "success",
            "result": analysis_result,
        })

        # ---------------------------------------------------------
        # 6. Deployment plan
        # ---------------------------------------------------------
        deployment_plan = self.deployment_planner_agent.execute(
            project_structure,
            application_details,
            analysis,
        )

        steps.append({
            "step": "deployment_plan",
            "status": "success",
            "result": deployment_plan,
        })

        # ---------------------------------------------------------
        # Extract service + health-check configuration
        # ---------------------------------------------------------
        services = deployment_plan.get(
            "services",
            [],
        )

        service = services[0] if services else {}

        port = service.get(
            "port",
            5000,
        )

        health_check = deployment_plan.get(
            "health_check",
            {},
        )

        health_path = health_check.get(
            "path",
            "/",
        )

        # ---------------------------------------------------------
        # 7. Generate Dockerfile
        # ---------------------------------------------------------
        docker_result = self.docker_generator_agent.generate(
            workspace,
            deployment_plan,
        )

        steps.append({
            "step": "docker_generation",
            "status": "success",
            "result": docker_result,
        })

        # ---------------------------------------------------------
        # 8. Validate
        # ---------------------------------------------------------
        validation_result = self.validator_agent.validate(
            workspace,
            deployment_plan,
        )

        steps.append({
            "step": "validation",
            "status": (
                "success"
                if validation_result.get("valid")
                else "failed"
            ),
            "result": validation_result,
        })

        if not validation_result.get("valid"):
            return {
                "status": "failed",
                "project_id": project_id,
                "stage": "validation",
                "deployment_type": "render",
                "steps": steps,
                "error": "Deployment validation failed.",
            }

        # ---------------------------------------------------------
        # 9. Build Docker image
        # ---------------------------------------------------------
        local_image = (
            f"agentic-deployment-{project_id}:latest"
        )

        build_result = self.docker_build_agent.build(
            project_path=workspace,
            image_name=local_image,
        )

        steps.append({
            "step": "docker_build",
            "status": build_result.get("status"),
            "result": build_result,
        })

        if build_result.get("status") != "success":
            return {
                "status": "failed",
                "project_id": project_id,
                "stage": "docker_build",
                "deployment_type": "render",
                "steps": steps,
                "error": "Docker image build failed.",
            }

        # ---------------------------------------------------------
        # 10. Push image to Docker Hub
        # ---------------------------------------------------------
        image_tag = project_id

        registry_result = self.docker_registry_agent.push(
            local_image=local_image,
            tag=image_tag,
        )

        steps.append({
            "step": "docker_push",
            "status": registry_result.get("status"),
            "result": registry_result,
        })

        if registry_result.get("status") != "success":
            return {
                "status": "failed",
                "project_id": project_id,
                "stage": "docker_push",
                "deployment_type": "render",
                "steps": steps,
                "error": "Docker image push failed.",
            }

        image_url = registry_result.get("image")

        if not image_url:
            return {
                "status": "failed",
                "project_id": project_id,
                "stage": "docker_push",
                "deployment_type": "render",
                "steps": steps,
                "error": "Docker image URL was not returned.",
            }

        # ---------------------------------------------------------
        # 11. Get Render workspace
        # ---------------------------------------------------------
        owner_id = (
            self.render_agent.service
            .get_first_workspace_id()
        )

        steps.append({
            "step": "render_workspace",
            "status": "success",
            "result": {
                "owner_id": owner_id,
            },
        })

        # ---------------------------------------------------------
        # 12. Create Render registry credential
        # ---------------------------------------------------------
        credential_result = (
            self.render_agent.create_registry_credential(
                owner_id=owner_id,
            )
        )

        steps.append({
            "step": "render_registry_credential",
            "status": credential_result.get("status"),
            "result": credential_result,
        })

        if credential_result.get("status") != "success":
            return {
                "status": "failed",
                "project_id": project_id,
                "stage": "render_registry_credential",
                "deployment_type": "render",
                "steps": steps,
                "error": (
                    "Render registry credential creation failed."
                ),
            }

        credential_id = credential_result.get(
            "credential_id"
        )

        if not credential_id:
            return {
                "status": "failed",
                "project_id": project_id,
                "stage": "render_registry_credential",
                "deployment_type": "render",
                "steps": steps,
                "error": (
                    "Render registry credential ID "
                    "was not returned."
                ),
            }

        # ---------------------------------------------------------
        # 13. Create Render image-backed service
        # ---------------------------------------------------------
        render_result = self.render_agent.deploy(
            image_path=image_url,
            service_name=(
                f"agentic-deployment-{project_id}"
            ),
            plan="free",
            region="singapore",
            health_check_path=health_path,
            owner_id=owner_id,
            registry_credential_id=credential_id,
        )

        steps.append({
            "step": "render_deployment",
            "status": render_result.get("status"),
            "result": render_result,
        })

        if render_result.get("status") != "success":
            return {
                "status": "failed",
                "project_id": project_id,
                "stage": "render_deployment",
                "deployment_type": "render",
                "steps": steps,
                "error": render_result.get(
                    "error",
                    "Render deployment failed.",
                ),
            }

        # ---------------------------------------------------------
        # 14. Cloud deployment successful
        # ---------------------------------------------------------
        service_url = render_result.get(
            "service_url"
        )

        return {
            "status": "success",
            "project_id": project_id,
            "stage": "cloud_deployed",
            "deployment_type": "render",
            "url": service_url,
            "service_url": service_url,
            "service_id": render_result.get(
                "service_id"
            ),
            "service_name": render_result.get(
                "service_name"
            ),
            "docker_image": image_url,
            "port": port,
            "health_check_path": health_path,
            "steps": steps,
        }

    # ============================================================
    # RENDER SERVICE STATUS
    # ============================================================

    def get_render_service(
        self,
        service_id: str,
    ) -> Dict[str, Any]:

        if not service_id:
            raise ValueError(
                "Render service ID is required."
            )

        return self.render_agent.get_service(
            service_id,
        )