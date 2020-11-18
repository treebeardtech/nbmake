from typing import Any, Optional

from pydantic import BaseModel


class GitHubDetails(BaseModel):
    sha: str
    branch: str
    workflow: str
    event_name: str
    event_path: str
    run_id: str
    user_name: str
    repo_short_name: str

    @property
    def run_path(self):
        return f"{self.user_name}/{self.repo_short_name}/{self.run_id}"


class NbMakeContext(BaseModel):
    api_key: Optional[str] = None  # Not present at build time
    kernel_name: str = "python3"
    cell_execution_timeout_seconds: int = 300
    debug: bool = False
    api_url: str
    filename: str
    github_details: Optional[GitHubDetails] = None

    def __str__(self) -> str:
        dict_obj: Any = self.dict()
        if self.api_key:
            unredacted_length = 4
            dict_obj["api_key"] = (
                "x" * (len(self.api_key) - unredacted_length)
                + self.api_key[-unredacted_length:]
            )
        return str(dict_obj)
