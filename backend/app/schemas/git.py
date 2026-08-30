from pydantic import BaseModel, HttpUrl


class GitCloneRequest(BaseModel):
    repository_url: HttpUrl