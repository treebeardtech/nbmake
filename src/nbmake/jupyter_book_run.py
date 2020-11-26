import json
import os
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

import jupyter_book
import yaml  # type: ignore
from jupyter_cache import get_cache  # type: ignore
from jupyter_cache.cache.main import JupyterCacheBase  # type: ignore

from .jupyter_book_result import JupyterBookResult
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
    cache: Optional[JupyterCacheBase] = None  # type: ignore

    def __init__(self, filename: Path, config_filename: Optional[Path] = None) -> None:
        self.filename = Path(filename)
        self.basename = Path(os.path.basename(self.filename))
        self.path_output = data_dir / str(uuid.uuid4())
        self.built_ipynb = (
            self.path_output
            / f"_build/_page/{str(self.basename).replace('.ipynb','')}/jupyter_execute/{self.basename}"
        )

        if config_filename:
            self.config = self.get_config(config_filename)  # type: ignore
            self.cache = get_cache(self.config["execute"]["cache"])  # type: ignore

    def get_config(self, config_filename: Path) -> Dict[Any, Any]:
        with open(config_filename) as conf:
            loaded: Any = yaml.load(conf, Loader=yaml.FullLoader)
            if not loaded:
                raise Exception("Failed to read jb config")

            default_cache_loc = (
                Path(os.path.dirname(config_filename)) / "_build/.jupyter_cache"
            )

            default_conf_override = {
                "execute": {
                    "execute_notebooks": "cache",
                    "cache": str(default_cache_loc),
                }
            }

            return {**loaded, **default_conf_override}

    def _get_executed_ipynb(self) -> Dict[Any, Any]:

        with open(self.built_ipynb) as j:
            x = json.loads(j.read())
            return x

    def _get_failing_cell_index(self, doc: Dict[Any, Any]) -> Optional[int]:
        code_cells = [cell for cell in doc["cells"] if cell["cell_type"] == "code"]
        for i, cell in enumerate(code_cells):
            errors = [
                output
                for output in cell["outputs"]
                if output["output_type"] == "error" or "ename" in output
            ]

            if errors:
                return i

        return None

    def rm_cache(self):
        if not self.cache:
            return
        matches = [r for r in self.cache.list_cache_records() if r.uri == self.filename]  # type: ignore

        if matches:
            self.cache.remove_cache(matches[0].pk)  # type: ignore

    def execute(self) -> JupyterBookResult:
        self.rm_cache()

        config_filename = Path(f"{tempfile.NamedTemporaryFile().name}.yml")
        with open(config_filename, "w") as yaml_file:
            yaml.dump(self.config or {}, yaml_file)

        out = subprocess.check_output(
            [
                JB_BINARY,
                "build",
                "--config",
                config_filename,
                "--path-output",
                self.path_output,
                self.filename,
            ],
        )
        print(out.decode())
        doc = self._get_executed_ipynb()
        failing_cell_index = self._get_failing_cell_index(doc)
        return JupyterBookResult(document=doc, failing_cell_index=failing_cell_index)
