import json
import os
import shutil
import subprocess
from pathlib import Path
from traceback import format_exc
from typing import Any, Dict, Optional

import papermill as pm  # type: ignore

from .. import helper
from ..conf import NbMakeContext
from ..helper import shell
from ..importchecker.imports import check_imports
from ..logs import log as tb_log
from ..logs.helpers import clean_log_file
from ..runtime.helper import (
    NotebookResult,
    get_failed_nb_details,
    get_health_bar,
    get_summary,
)

bucket_name = "nbmake-notebook-outputs"


status_emojis = {
    "SUCCESS": "✅",
    "WORKING": "⏳",
    "FAILURE": "💥",
    "TIMEOUT": "⏰",
}


class NotebookRun:
    _nbmake_context: NbMakeContext
    _run_path: Optional[str] = None
    _web_api_callback: Optional[helper.WebAPICallback] = None

    def __init__(self, nbmake_context: NbMakeContext) -> None:
        self._nbmake_context = nbmake_context
        if self._nbmake_context.github_details and self._nbmake_context.api_key:
            self._run_path = self._nbmake_context.github_details.run_path

            self._web_api_callback = helper.WebAPICallback(
                self._nbmake_context.github_details, self._nbmake_context
            )

    def upload_nb(self, run_path: str, nb_status: str, set_as_thumbnail: bool):
        notebook_path = self._nbmake_context.filename
        notebook_upload_path = f"{run_path}/{notebook_path}"

        self._web_api_callback and self._web_api_callback.upload_artifact(
            notebook_path,
            notebook_upload_path,
            nb_status,
            set_as_thumbnail=set_as_thumbnail,
        )

    def upload_outputs(self, run_path: str):
        output_dir = os.path.dirname(self._nbmake_context.filename)
        for root, _, files in os.walk(output_dir, topdown=False):
            for name in files:
                full_name = os.path.join(root, name)
                upload_path = f"{run_path}/{full_name}"
                self._web_api_callback and self._web_api_callback.upload_artifact(
                    full_name, upload_path, None
                )

    def run_notebook(self, notebook_path: str) -> NotebookResult:
        def get_nb_dict():
            with open(notebook_path) as json_file:
                return json.load(json_file)

        try:
            notebook_dir, notebook_name = os.path.split(notebook_path)
            helper.log(
                f"Executing Notebook {notebook_name} in {'.' if len(notebook_dir) == 0 else notebook_dir}"
            )

            kernel_name = self._nbmake_context.kernel_name

            venv_activate_script = ""
            if kernel_name.startswith("python"):

                nb_kernel_name = "_" + notebook_name.replace(".ipynb", "").replace(
                    "/", "_"
                )
                venv_path = Path(f"venvs/{nb_kernel_name}")

                if os.name == "nt":
                    venv_activate_script = f". {venv_path}\\Scripts\\activate.ps1"
                else:
                    venv_activate_script = f". {venv_path}/bin/activate"

                shutil.rmtree(venv_path, ignore_errors=True)
                create_venv_cmd = f"virtualenv --system-site-packages {venv_path}"
                create_kernel_cmd = f"{venv_activate_script}; python -m ipykernel install --user --name {nb_kernel_name}"

                shell(create_venv_cmd)
                shell(create_kernel_cmd)
                kernel_name = nb_kernel_name

            pm_cmd = f"""
{venv_activate_script}; \
papermill \
  --kernel {kernel_name} \
  --no-progress-bar \
  --request-save-on-cell-execute \
  --autosave-cell-every 10 \
  --execution-timeout {self._nbmake_context.cell_execution_timeout_seconds} \
  --log-output \
  --cwd {os.getcwd()}/{notebook_dir} \
  {notebook_path} \
  {notebook_path}
"""
            shell(pm_cmd)

            helper.log(f"{status_emojis['SUCCESS']} Notebook {notebook_path} passed!\n")
            nb_dict = get_nb_dict()
            num_cells = len(nb_dict["cells"])
            return NotebookResult(
                status="SUCCESS",
                num_cells=num_cells,
                num_passing_cells=num_cells,
                err_line="",
            )
        except Exception:
            tb = format_exc()
            nb_dict = get_nb_dict()
            num_cells = len(nb_dict["cells"])
            err_line, num_passing_cells, status = get_failed_nb_details(
                nb_dict, self._nbmake_context
            )

            helper.log(
                f"""{status_emojis[status]} Notebook {notebook_path} failed!\n  {num_passing_cells}/{num_cells} cells ran.\n\n{tb}"""
            )

            return NotebookResult(
                status=status,
                num_cells=num_cells,
                num_passing_cells=num_passing_cells,
                err_line=err_line,
            )

    def _run(self,) -> Dict[str, NotebookResult]:
        helper.log(f"🌲 nbmake runtime: running repo")

        if self._nbmake_context.debug:
            subprocess.run(
                [
                    "bash",
                    "-c",
                    """
                    echo "working directory is $(pwd)\n\n$(ls -la)\n"
                    """,
                ]
            )

        if self._nbmake_context is None:
            raise Exception("No nbmake Config Present at runtime!")

        notebook_files = [self._nbmake_context.filename]
        notebook_results: Dict[Any, Any] = {
            notebook: NotebookResult(
                status="WORKING", num_cells=1, num_passing_cells=1, err_line=""
            )
            for notebook in notebook_files
        }
        print(f"Will run the following:")
        [print(f" - {nb}") for nb in notebook_files]
        print()

        set_as_thumbnail = True
        for i, notebook_path in enumerate(notebook_files):
            helper.log(
                f"{status_emojis['WORKING']} Running {i + 1}/{len(notebook_files)}: {notebook_path}"
            )
            result = self.run_notebook(notebook_path)
            notebook_results[notebook_path] = result
            if self._run_path:
                self.upload_nb(
                    self._run_path, result.status, set_as_thumbnail,
                )
            set_as_thumbnail = False

        return notebook_results

    def finish(
        self, status: int, results: str, logging: bool,
    ):
        def get_status_str():
            if status == 0:
                return "SUCCESS"
            else:
                return "FAILURE"

        print(results)

        self._web_api_callback and self._web_api_callback.update(
            update_url=f"{self._nbmake_context.api_url}/{self._run_path}/log",
            status=get_status_str(),
        )

        if os.path.exists("nbmake.log"):
            self._web_api_callback and self._web_api_callback.upload_artifact(
                "nbmake.log", f"{self._run_path}/nbmake.log", None,
            )

            with open("tb_results.log", "w", encoding="utf-8") as results_log:
                results_log.write(results)

            self._web_api_callback and self._web_api_callback.upload_artifact(
                "tb_results.log", f"{self._run_path}/__nbmake__/tb_results.log", None,
            )
            self._web_api_callback and self._web_api_callback.update(
                update_url=f"{self._nbmake_context.api_url}/{self._run_path}/update",
                status=get_status_str(),
            )
            print(f"🌲 View your outputs at https://nbmake.io/admin/{self._run_path}")

        return status

    def start(self, logging: bool = True):
        clean_log_file()

        notebook_results = self._run()

        if self._run_path:
            self.upload_outputs(self._run_path)

        helper.log("🌲 Run Finished. Results:\n")

        results = ""
        for notebook in notebook_results.keys():
            result = notebook_results[notebook]
            health_bar = get_health_bar(
                result.num_passing_cells, result.num_cells, result.status, status_emojis
            )

            if result.status == "SUCCESS":
                results += f"{health_bar} {notebook}\n"
                results += (
                    f"  ran {result.num_passing_cells} of {result.num_cells} cells\n"
                )
            elif not result.err_line:  # failed to parse notebook properly
                results += f"{status_emojis[result.status]} {notebook}"
            else:
                results += f"{health_bar} {notebook}\n"
                results += (
                    f"  ran {result.num_passing_cells} of {result.num_cells} cells\n"
                )
                results += f"  {status_emojis[result.status]} {result.err_line}\n"

            results += "\n"

        n_passed = len(
            list(filter(lambda v: v.status == "SUCCESS", notebook_results.values()))
        )

        total_nbs = len(notebook_results)
        if n_passed < total_nbs:
            summary_block = get_summary(notebook_results, n_passed, total_nbs)
            results += summary_block + "\n"
            tb_log(summary_block, print_content=False)

            try:
                if self._nbmake_context.kernel_name == "python3":
                    _, import_checker_output = check_imports()
                    results += import_checker_output
                    results += "\n"
            except Exception as ex:
                print(f"Import checker encountered and error...\n{ex}")

            fail_status = 2 if self._run_path else 1
            return self.finish(fail_status, results, logging)
        else:
            return self.finish(0, results, logging)
