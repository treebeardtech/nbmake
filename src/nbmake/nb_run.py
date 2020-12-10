import traceback
from pathlib import Path
from typing import Any, Dict, Optional

import nbformat
from jupyter_cache.cache.main import JupyterCacheBase
from nbclient.client import (
    CellExecutionError,
    CellTimeoutError,
    NotebookClient,
)
from nbformat import NotebookNode

from .nb_result import NotebookError, NotebookResult

NB_VERSION = 4


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
        cache: JupyterCacheBase = None,
        verbose: bool = False,
    ) -> None:
        self.filename = Path(filename)
        self.path_output = path_output
        self.cache = cache
        self.verbose = verbose

    def execute(
        self,
    ) -> NotebookResult:
        nb = nbformat.read(str(self.filename), NB_VERSION)
        timeout = 300
        allow_errors = False
        if "execution" in nb.metadata:
            if "timeout" in nb.metadata.execution:
                timeout = nb.metadata.execution.timeout
            if "allow_errors" in nb.metadata.execution:
                allow_errors = nb.metadata.execution.allow_errors

        error: Optional[NotebookError] = None
        try:
            c = NotebookClient(
                nb,
                timeout=timeout,
                allow_errors=allow_errors,
                record_timing=True,
            )
            c.execute(cwd=self.filename.parent)
        except CellExecutionError:
            exc_string = "".join(traceback.format_exc())
            error = self._get_error(nb)
            print(exc_string)
        except CellTimeoutError as err:
            trace = err.args[0]
            error = NotebookError(
                summary=trace.split("\n")[0],
                trace=trace,
                failing_cell_index=self._get_timeout_cell(nb),
            )

        built_ipynb = self.path_output / self.filename
        built_ipynb.parent.mkdir(exist_ok=True, parents=True)
        nbformat.write(nb, str(built_ipynb))
        if self.cache:
            self.cache.cache_notebook_file(
                built_ipynb, check_validity=False, overwrite=True
            )

        return NotebookResult(nb=nb, error=error)

    def _get_timeout_cell(self, nb: NotebookNode) -> int:
        for i, cell in enumerate(nb.cells):
            if cell.cell_type != "code":
                continue
            if "shell.execute_reply" not in cell.metadata.execution:
                return i

        return -1

    def _get_error(self, nb: NotebookNode) -> Optional[NotebookError]:
        for i, cell in reversed(list(enumerate(nb["cells"]))):  # get LAST error
            if cell["cell_type"] != "code":
                continue
            errors = [
                output
                for output in cell["outputs"]
                if output["output_type"] == "error" or "ename" in output
            ]

            if errors:
                num_cells = len(nb["cells"])
                tb = "\n".join(errors[0].get("traceback", ""))
                last_trace = tb.split("\n")[-1]
                summary = f"cell {i + 1} of {num_cells}: {last_trace}"
                trace = f"{summary}:\n{tb}"
                return NotebookError(summary=summary, trace=trace, failing_cell_index=i)

        return None
