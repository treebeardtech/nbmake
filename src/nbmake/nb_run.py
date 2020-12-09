import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from jupyter_cache.cache.main import JupyterCacheBase

from .jupyter_book_adapter import build
from .nb_result import NotebookError, NotebookResult


class NotebookRun:
    filename: Path
    basename: Path
    built_ipynb: Path
    config: Dict[Any, Any]
    cache: JupyterCacheBase
    path_output: Path
    verbose: bool

    def __init__(
        self,
        filename: Path,
        path_output: Path,
        cache: JupyterCacheBase,
        config_filename: Optional[Path] = None,
        verbose: bool = False,
    ) -> None:
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
        self.verbose = verbose

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

    def _get_error(self, doc: Dict[Any, Any]) -> Optional[NotebookError]:
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
                return NotebookError(summary=summary, trace=trace, failing_cell_index=i)

        return None

    def execute(self) -> NotebookResult:
        (self.path_output / "_build").mkdir(exist_ok=True, parents=True)
        config_filename = Path(self.path_output / "_build" / "_config.yml")
        config_filename.write_text(yaml.dump(self.config))

        build(self.filename, self.path_output, config_filename, verbose=self.verbose)

        self.cache.cache_notebook_file(
            self.built_ipynb, check_validity=False, overwrite=True
        )

        doc = self._get_executed_ipynb()
        err = self._get_error(doc)
        return NotebookResult(document=doc, error=err)
