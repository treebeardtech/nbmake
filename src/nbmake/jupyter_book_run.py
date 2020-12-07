import json
import os
import subprocess
from pathlib import Path
from subprocess import CalledProcessError
from typing import Any, Dict, List, Optional

import jupyter_book
import yaml
from jupyter_cache.cache.main import JupyterCacheBase

from .jupyter_book_result import JupyterBookError, JupyterBookResult

jb_path: str = jupyter_book.__file__
JB_BINARY: Path = (
    Path(os.path.dirname(jb_path))
    / ("../../../Scripts/jb.exe" if os.name == "nt" else "../../../../bin/jb")
).resolve()


class JupyterBookRun:
    filename: Path
    basename: Path
    built_ipynb: Path
    config_filename: Path
    config: Dict[Any, Any]
    cache: JupyterCacheBase
    path_output: Path

    def __init__(
        self,
        filename: Path,
        path_output: Path,
        cache: JupyterCacheBase,
        config_filename: Optional[Path] = None,
    ) -> None:
        # TODO validate input paths
        self.filename = Path(filename)
        self.basename = Path(os.path.basename(self.filename))
        self.path_output = path_output
        self.built_ipynb = (
            self.path_output
            / f"_build/_page/{str(self.basename).replace('.ipynb','')}/jupyter_execute/{self.basename}"
        )

        user_config = self.get_user_config(config_filename)
        self.config = self.get_config(user_config)
        self.cache = cache

    def get_user_config(
        self, config_filename: Optional[Path]
    ) -> Optional[Dict[Any, Any]]:
        if not config_filename:
            return None

        loaded: Dict[Any, Any] = yaml.load(config_filename.read_text())
        if not loaded:
            raise Exception("Failed to read jb config")
        return loaded

    def get_config(self, user_config: Optional[Dict[Any, Any]]) -> Dict[Any, Any]:
        loaded: Dict[Any, Any] = {}
        if not user_config is None:
            loaded = user_config
        loaded["execute"] = loaded.get("execute", {})
        loaded["execute"]["execute_notebooks"] = "force"
        loaded["execute"]["cache"] = None
        return loaded

    def _get_executed_ipynb(self) -> Dict[Any, Any]:
        return json.loads(self.built_ipynb.read_text())

    def _get_error(self, doc: Dict[Any, Any]) -> Optional[JupyterBookError]:
        for i, cell in enumerate(doc["cells"]):
            if cell["cell_type"] != "code":
                continue
            errors = [
                output
                for output in cell["outputs"]
                if output["output_type"] == "error" or "ename" in output
            ]

            if errors:
                num_cells = len(doc["cells"])
                tb = "\n".join(errors[0].get("traceback", ""))
                last_trace = tb.split("\n")[-1]
                summary = f"cell {i + 1} of {num_cells}: {last_trace}"
                trace = f"{summary}:\n{tb}"
                return JupyterBookError(
                    summary=summary, trace=trace, failing_cell_index=i
                )

        return None

    def execute(self) -> JupyterBookResult:
        self.path_output.mkdir(exist_ok=True, parents=True)
        config_filename = Path(self.path_output / "_config.yml")
        config_filename.write_text(yaml.dump(self.config))

        args: List[str] = [
            str(JB_BINARY),
            "build",
            # "-W",
            "--config",
            str(config_filename),
            "--path-output",
            str(self.path_output),
            str(self.filename),
        ]
        try:
            print(f"\nnbmake: Running {' '.join(args)}")
            subprocess.check_output(args, stderr=subprocess.STDOUT)
            # print(out.decode()) tODO log
        except CalledProcessError as err:
            print(
                f"\nnbmake: the jupyter-book command failed.\n\n{err.output.decode()}"
            )

        self.cache.cache_notebook_file(
            self.built_ipynb, check_validity=False, overwrite=True
        )

        doc = self._get_executed_ipynb()
        err = self._get_error(doc)
        return JupyterBookResult(document=doc, error=err)
