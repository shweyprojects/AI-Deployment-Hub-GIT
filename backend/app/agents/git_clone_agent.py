from app.services.git_service import GitService


class GitCloneAgent:

    def __init__(self):
        self.git_service = GitService()

    def execute(
        self,
        repository_url: str,
        project_id: str | None = None,
    ):
        return self.git_service.clone_repository(
            repository_url,
            project_id,
        )
