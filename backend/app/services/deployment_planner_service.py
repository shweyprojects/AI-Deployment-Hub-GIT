import json

from app.services.ollama_service import OllamaService


class DeploymentPlannerService:

    def __init__(self):
        self.ollama_service = OllamaService()

    def create_plan(
        self,
        project_structure: dict,
        application_details: dict,
        analysis: str
    ):

        prompt = f"""
You are a deployment planning agent.

Create a deployment plan for the project using ONLY the
information provided below.

PROJECT STRUCTURE:
{json.dumps(project_structure, indent=2)}

APPLICATION DETAILS:
{json.dumps(application_details, indent=2)}

AI PROJECT ANALYSIS:
{analysis}

Return ONLY valid JSON.

Use exactly this structure:

{{
    "project_type": "",
    "framework": "",
    "deployment_type": "docker",
    "services": [
        {{
            "name": "",
            "port": 0,
            "start_command": "",
            "docker_required": true
        }}
    ],
    "health_check": {{
        "path": "/",
        "port": 0
    }},
    "deployment_steps": []
}}

Do not include markdown.
Do not include explanations outside the JSON.
Do not invent services or ports.
"""

        response = self.ollama_service.generate(prompt)

        return self._parse_response(response)

    def _parse_response(self, response: str):

        response = response.strip()

        if response.startswith("```"):
            response = response.replace("```json", "")
            response = response.replace("```", "")
            response = response.strip()

        try:
            return json.loads(response)

        except json.JSONDecodeError:

            return {
                "error": "AI returned invalid JSON",
                "raw_response": response
            }