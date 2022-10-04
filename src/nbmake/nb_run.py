from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from contextlib import asynccontextmanager

import nbformat
from nbclient.client import (
    CellExecutionError,
    CellTimeoutError,
    NotebookClient,
)
from nbclient.util import run_sync
from nbformat import NotebookNode
import jupytext


from .nb_result import NotebookError, NotebookResult

NB_VERSION = 4


def convert_and_read_notebook(filename: str) -> NotebookNode:
    """Read a notebook, potentially converting from various jupytext formats."""
    ext = Path(filename).suffix
    if ext == ".ipynb":
        nb = nbformat.read(filename, NB_VERSION)
    else:
        # Attempt to convert the notebook using Jypytext.
        nb = jupytext.read(filename)
    return nb


class NotebookRun:
    filename: Path
    verbose: bool

    def __init__(
        self,
        filename: Path,
        default_timeout: int,
        verbose: bool = False,
        kernel: Optional[str] = None,
        cell_indices: Optional[List[int]] = None,
    ) -> None:
        self.filename = filename
        self.verbose = verbose
        self.default_timeout = default_timeout
        self.kernel = kernel

        # Note: if 'cell_indices' is None, the entire notebook is executed as
        # one. Otherwise the subset of given cell inidces is executed.
        self.cell_indices: Optional[List[int]] = cell_indices

    def execute(self) -> NotebookResult:
        nb = convert_and_read_notebook(str(self.filename))

        for cell in nb.cells:
            if cell.cell_type == "code":
                cell.outputs = []
        timeout = self.default_timeout
        allow_errors = False
        if "execution" in nb.metadata:
            if "timeout" in nb.metadata.execution:
                timeout = nb.metadata.execution.timeout
            if "allow_errors" in nb.metadata.execution:
                allow_errors = nb.metadata.execution.allow_errors

        error: Optional[NotebookError] = None

        extra_kwargs = {}
        if self.kernel:
            extra_kwargs["kernel_name"] = self.kernel

        try:
            c = NotebookClient(
                nb,
                timeout=timeout,
                allow_errors=allow_errors,
                record_timing=True,
                **extra_kwargs,
            )

            async def apply_mocks(
                cell: NotebookNode, cell_index: int, execute_reply: Dict[str, Any]
            ):
                # https://github.com/treebeardtech/nbmake/issues/77
                if any(o["output_type"] == "error" for o in cell["outputs"]):
                    execute_reply["content"]["status"] = "error"

                if c.kc is None:
                    raise Exception("there is no kernelclient")
                mocks: Dict[str, Any] = (
                    cell.get("metadata", {}).get("nbmake", {}).get("mock", {})
                )
                for v in mocks:
                    if isinstance(mocks[v], str):
                        out = await c.kc.execute_interactive(f"{v} = '{mocks[v]}'")
                    else:
                        out = await c.kc.execute_interactive(f"{v} = {mocks[v]}")

                    if out["content"]["status"] != "ok":
                        raise Exception(f"Failed to apply mock {v}\n\n{str(out)}")

            c.on_cell_executed = apply_mocks

            if self.cell_indices is None:
                # Run the entire notebook.
                c.execute(cwd=self.filename.parent)
            else:
                # Run the given subset of cells in `self.cell_indices`.
                async def execute_cells():
                    async with c.async_setup_kernel(cwd=self.filename.parent):
                        for cell_index in self.cell_indices:
                            cell = nb.cells[cell_index]
                            try:
                                res = c.execute_cell(cell=cell, cell_index=cell_index)
                            except Exception as exc:
                                exc.cell_index = cell_index
                                raise exc

                run_sync(execute_cells)()
        except CellExecutionError as exc:
            error = (
                _get_error(nb)
                if self.cell_indices is None
                else _get_error_for_cell(nb, exc.cell_index)
            )
        except CellTimeoutError as err:
            trace = err.args[0]
            error = NotebookError(
                summary=trace.split("\n")[0],
                trace=trace,
                failing_cell_index=_get_timeout_cell(nb),
            )
        except Exception as err:
            # if at top causes https://github.com/jupyter/nbclient/issues/128
            # from jupyter_client.kernelspec import KernelSpecManager, NoSuchKernel
            # trace=f"{summary}\n\nInstalled Kernels: {str(KernelSpecManager().find_kernel_specs())}",
            # https://github.com/treebeardtech/nbmake/runs/1536896858?check_suite_focus=true
            if str(type(err)) != "<class 'jupyter_client.kernelspec.NoSuchKernel'>":
                raise err

            summary = f"Error - No such kernel: '{err.name}'"  # type: ignore
            error = NotebookError(
                summary=summary,
                trace=f"{summary}",
                failing_cell_index=0,
            )

        return NotebookResult(nb=nb, error=error)


def _get_timeout_cell(nb: NotebookNode) -> int:
    for i, cell in enumerate(nb.cells):
        if cell.cell_type != "code":
            continue
        if "shell.execute_reply" not in cell.metadata.execution:
            return i

    return -1


def _get_error(nb: NotebookNode) -> Optional[NotebookError]:
    for i, cell in reversed(list(enumerate(nb["cells"]))):  # get LAST error
        if cell["cell_type"] != "code":
            continue
        errors = [
            output
            for output in cell["outputs"]
            if output["output_type"] == "error" or "ename" in output
        ]

        if errors:
            tb = "\n".join(errors[0].get("traceback", ""))
            src = "".join(cell["source"])
            last_trace = tb.split("\n")[-1]
            line = 75 * "-"
            trace = f"{line}\n{src}\n{tb}"
            return NotebookError(summary=last_trace, trace=trace, failing_cell_index=i)

    return None


def _get_error_for_cell(nb: NotebookNode, cell_index: int) -> Optional[NotebookError]:
    cell = nb.cells[cell_index]
    assert cell["cell_type"] == "code"

    errors = [
        output
        for output in cell["outputs"]
        if output["output_type"] == "error" or "ename" in output
    ]

    if errors:
        tb = "\n".join(errors[0].get("traceback", ""))
        src = "".join(cell["source"])
        last_trace = tb.split("\n")[-1]
        line = 75 * "-"
        trace = f"{line}\n{src}\n{tb}"
        return NotebookError(
            summary=last_trace, trace=trace, failing_cell_index=cell_index
        )

    return None
