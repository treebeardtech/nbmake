import datetime
import json
import mimetypes
import os
import subprocess
from typing import Any, Dict, List, Optional

import requests
from requests import Response

from .conf import GitHubDetails, NbMakeContext


def log(message: str):
    print(f'{datetime.datetime.now().strftime("%H:%M:%S")}: {message}')


def get_time():
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def shell(command: str):
    shell_cmd: List[str] = (
        ["powershell", "-command"] if os.name == "nt" else ["bash", "-c",]
    )
    subprocess.check_output(shell_cmd + [command])


class WebAPICallback:
    _github_details: GitHubDetails
    _nbmake_context: NbMakeContext
    debug: bool

    def __init__(
        self, github_details: GitHubDetails, nbmake_context: NbMakeContext
    ) -> None:
        self._github_details = github_details
        self._nbmake_context = nbmake_context

    def update(self, update_url: str, status: Optional[str] = None):
        data: Dict[Any, Any] = {}
        if status:
            data["status"] = status

        github_details = self._github_details
        data["workflow"] = (
            github_details.workflow.replace(".yml", "")
            .replace(".yaml", "")
            .split("/")[-1]
        )

        data["event_name"] = github_details.event_name
        if github_details.event_name == "push" and os.path.exists(
            github_details.event_path
        ):
            with open(github_details.event_path, "r") as event:
                event_json = json.load(event)
                data["sender"] = event_json["sender"]
                data["head_commit"] = event_json["head_commit"]

        data["sha"] = github_details.sha
        data["branch"] = github_details.branch

        data["start_time"] = os.getenv("nbmake_START_TIME") or get_time()
        if status in ["SUCCESS", "FAILURE"]:
            data["end_time"] = get_time()

        resp = requests.post(  # type:ignore
            update_url, json=data, headers={"api_key": self._nbmake_context.api_key},
        )

        if self.debug:
            print(f"Updating backend with data\n{data}")

    def upload_artifact(
        self,
        filename: str,
        upload_path: str,
        status: Optional[str],
        set_as_thumbnail: bool = False,
    ):
        log(f"Uploading {filename} to {upload_path}\n")
        content_type: str = str(mimetypes.guess_type(filename)[0])
        get_url_params = {"content_type": content_type}
        put_object_headers = {"Content-Type": content_type}
        if status:
            get_url_params["status"] = status
            put_object_headers["x-goog-meta-status"] = status

        with open(filename, "rb") as data:
            resp: Response = requests.get(  # type: ignore
                f"{self._nbmake_context.api_url}/get_upload_url/{upload_path}",
                params=get_url_params,
            )
            if resp.status_code != 200:
                msg = f"Get signed url failed for {filename}, {resp.status_code}\n{resp.text}"
                raise (Exception(msg))
            signed_url: str = resp.text
            put_resp = requests.put(
                signed_url, data, headers=put_object_headers,
            )  # type: ignore
            if put_resp.status_code != 200:
                msg = f"Put object failed for {filename}, {put_resp.status_code}\n{put_resp.text}"
                raise (Exception(msg))

            qs = "set_as_thumbnail=true" if set_as_thumbnail else ""
            extras_resp = requests.post(f"{api_url}/{upload_path}/create_extras?{qs}")  # type: ignore
            if put_resp.status_code != 200:
                msg = f"Extras failed for {filename}, {extras_resp.status_code}\n{extras_resp.text}"

        self.update(
            update_url=f"{self._nbmake_context.api_url}/{self._github_details.run_path}/update"
        )


def create_github_details():
    run_id = os.getenv("GITHUB_RUN_ID")

    if not run_id:
        return None

    sha = os.environ["GITHUB_SHA"]
    ref = os.environ["GITHUB_REF"]
    workflow = os.environ["GITHUB_WORKFLOW"]
    event_name = os.environ["GITHUB_EVENT_NAME"]
    event_path = os.environ["GITHUB_EVENT_PATH"]

    branch = ref.split("/")[-1]
    user_name = os.environ["GITHUB_REPOSITORY"].split("/")[0]
    repo_short_name = os.environ["GITHUB_REPOSITORY"].split("/")[1]

    return GitHubDetails(
        run_id=run_id,
        sha=sha,
        branch=branch,
        repo_short_name=repo_short_name,
        user_name=user_name,
        event_name=event_name,
        event_path=event_path,
        workflow=workflow,
    )
