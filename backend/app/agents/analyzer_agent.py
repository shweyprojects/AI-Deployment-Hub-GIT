import json

from app.services.ollama_service import OllamaService


class AnalyzerAgent:

    def __init__(self):
        self.ollama_service = OllamaService()

    def execute(
        self,
        project_structure: dict,
        application_details: dict
    ):

        prompt = f"""
You are a software project analysis agent.

Analyze the following project information.

PROJECT STRUCTURE:
{json.dumps(project_structure, indent=2)}

APPLICATION DETAILS:
{json.dumps(application_details, indent=2)}

Determine:

1. Project type
2. Application architecture
3. Number of applications/services
4. Frameworks
5. Dependencies
6. How the application should be run
7. Docker requirements
8. Important deployment considerations

Return a clear technical analysis.
Do not invent information that is not available.
"""

        analysis = self.ollama_service.generate(prompt)

        return {
            "analysis": analysis
        }