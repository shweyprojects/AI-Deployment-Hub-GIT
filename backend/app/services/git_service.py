import os
import uuid
from git import Repo


class GitService:

    def clone_repository(self, repository_url: str):
        project_id = str(uuid.uuid4())
        workspace = os.path.join("workspaces", project_id)

        os.makedirs(workspace, exist_ok=True)

        Repo.clone_from(repository_url, workspace)

        return {
            "project_id": project_id,
            "workspace": workspace,
            "repository_url": repository_url
        }