import json
import os
import subprocess
import tempfile
import uuid
from pathlib import Path
from subprocess import CalledProcessError
from typing import Any, Dict, List, Optional

import jupyter_book
import yaml  # type: ignore
from jupyter_cache import get_cache  # type: ignore
from jupyter_cache.cache.main import JupyterCacheBase  # type: ignore

from .jupyter_book_result import JupyterBookError, JupyterBookResult
from .util import data_dir

JB_BINARY: Path = (
    Path(os.path.dirname(jupyter_book.__file__))
    / ("../../../Scripts/jb.exe" if os.name == "nt" else "../../../../bin/jb")
).resolve()


class JupyterBookRun:
    filename: Path
    basename: Path
    built_ipynb: Path
    config: Optional[Dict[Any, Any]] = None
    cache: JupyterCacheBase  # type: ignore

    def __init__(self, filename: Path, config_filename: Optional[Path] = None) -> None:
        # TODO validate input paths
        self.filename = Path(filename)
        self.basename = Path(os.path.basename(self.filename))
        self.path_output = data_dir / str(uuid.uuid4())
        self.built_ipynb = (
            self.path_output
            / f"_build/_page/{str(self.basename).replace('.ipynb','')}/jupyter_execute/{self.basename}"
        )

        user_config = self.get_user_config(config_filename)
        self.config = self.get_config(user_config)  # type: ignore
        self.cache = get_cache(self.path_output / "_build/.jupyter_cache")  # type: ignore

    def get_user_config(self, config_filename: Optional[Path]) -> Optional[dict]:
        if not config_filename:
            return None

        with open(config_filename) as conf:
            loaded: Any = yaml.load(conf, Loader=yaml.FullLoader)
            if not loaded:
                raise Exception("Failed to read jb config")
        return loaded

    def get_config(self, user_config: Optional[dict]):
        loaded = dict(user_config or {})  # type: ignore
        loaded["execute"] = loaded.get("execute", {})
        loaded["execute"]["execute_notebooks"] = "force"
        return loaded

    def _get_executed_ipynb(self) -> Dict[Any, Any]:

        with open(self.built_ipynb) as j:
            x = json.loads(j.read())
            return x

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

    def rm_cache(self):
        if not self.cache:
            return
        matches = [r for r in self.cache.list_cache_records() if r.uri == str(self.filename.absolute())]  # type: ignore

        if matches:
            self.cache.remove_cache(matches[0].pk)  # type: ignore

    def execute(self) -> JupyterBookResult:
        self.rm_cache()

        config_filename = Path(f"{tempfile.NamedTemporaryFile().name}.yml")
        with open(config_filename, "w") as yaml_file:
            yaml.dump(self.config or {}, yaml_file)

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
            out = subprocess.check_output(args, stderr=subprocess.STDOUT)
            print(out.decode())
        except CalledProcessError as err:
            print(err.output.decode())

        self.cache.cache_notebook_file(self.built_ipynb, check_validity=False)

        doc = self._get_executed_ipynb()
        err = self._get_error(doc)
        return JupyterBookResult(document=doc, error=err)
