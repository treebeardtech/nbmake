from pathlib import Path
from typing import Any, Dict, Optional

import nbformat
from nbclient.client import (
    CellExecutionError,
    CellTimeoutError,
    NotebookClient,
)
from nbformat import NotebookNode

from .nb_result import NotebookError, NotebookResult

NB_VERSION = 4


class CellImportError(Exception):
    pass


class NotebookRun:
    filename: Path
    verbose: bool

    def __init__(
        self,
        filename: Path,
        default_timeout: int,
        verbose: bool = False,
        kernel: Optional[str] = None,
        find_import_errors: bool = False,
    ) -> None:
        self.filename = filename
        self.verbose = verbose
        self.default_timeout = default_timeout
        self.kernel = kernel
        self.find_import_errors = find_import_errors

    def execute(
        self,
    ) -> NotebookResult:
        nb = nbformat.read(str(self.filename), NB_VERSION)

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
                allow_errors=allow_errors or self.find_import_errors,
                interrupt_on_timeout=self.find_import_errors,
                record_timing=True,
                **extra_kwargs,
            )

            async def apply_mocks(
                cell: NotebookNode, cell_index: int, execute_reply: Dict[str, Any]
            ):
                # https://github.com/treebeardtech/nbmake/issues/77
                if any(o["output_type"] == "error" for o in cell["outputs"]):
                    execute_reply["content"]["status"] = "error"

                    if "ename" in execute_reply["content"]:
                        if execute_reply["content"]["ename"] == "ModuleNotFoundError":
                            if self.find_import_errors:
                                raise CellImportError()

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

            c.execute(cwd=self.filename.parent)
        except CellImportError:
            error = self._get_error(nb)
        except CellExecutionError:
            error = self._get_error(nb)
        except CellTimeoutError as err:
            trace = err.args[0]
            error = NotebookError(
                summary=trace.split("\n")[0],
                trace=trace,
                failing_cell_index=self._get_timeout_cell(nb),
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
                tb = "\n".join(errors[0].get("traceback", ""))
                src = "".join(cell["source"])
                last_trace = tb.split("\n")[-1]
                line = 75 * "-"
                trace = f"{line}\n{src}\n{tb}"
                return NotebookError(
                    summary=last_trace, trace=trace, failing_cell_index=i
                )

        return None
