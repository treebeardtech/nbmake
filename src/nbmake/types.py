from typing import Any, Dict, List

from pydantic import BaseModel


class Artifact(BaseModel):
    content_type: str
    name: str
    size: str


class Run(BaseModel):
    start_time: str
    end_time: str = ""
    run_id: str
    artifacts: List[Artifact]
    status: str
    trigger: Dict[str, Any] = {"mechanism": ""}
    url: str
