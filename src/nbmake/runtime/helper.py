from typing import Any, Dict, Optional, Tuple

from pydantic import BaseModel

from ..conf import NbMakeContext


class NotebookResult(BaseModel):  # type: ignore
    status: str
    num_cells: int
    num_passing_cells: int
    err_line: str


def get_failed_nb_details(
    nb_dict: Any, nbmake_context: NbMakeContext
) -> Tuple[str, int, str]:
    status = "FAILURE"
    num_passing_cells: Optional[int] = 0
    err_line = ""
    try:
        for cell in nb_dict["cells"]:
            if "outputs" in cell:
                errors = [
                    output
                    for output in cell["outputs"]
                    if output["output_type"] == "error" or "ename" in output
                ]
                if errors:
                    err_line = errors[0]["traceback"][-1]
                    break

                if (
                    "metadata" in cell
                    and "papermill" in cell["metadata"]
                    and "duration" in cell["metadata"]["papermill"]
                    and cell["metadata"]["papermill"]["duration"] == None
                ):
                    num_passing_cells -= 1
                    print("timeout")
                    err_line = f"Cell timed out after {nbmake_context.cell_execution_timeout_seconds}s. You can set `cell_execution_timeout_seconds` in nbmake.yaml."
                    status = "TIMEOUT"
                    break

                num_passing_cells += 1

    except Exception as ex:
        print(ex)

    return err_line, num_passing_cells, status


def get_health_bar(
    passing: int, total: int, status: str, status_emojis: Dict[str, str]
):
    assert passing <= total
    bar_length = 10
    n_green = int(bar_length * float(passing) / float(total))
    n_red = bar_length - n_green
    if n_green == bar_length:
        return "🟩" * (bar_length - 1) + status_emojis["SUCCESS"]
    return ("🟩" * n_green) + status_emojis[status] + ("⬜" * (n_red - 1))


def get_summary(
    notebook_results: Dict[str, NotebookResult], n_passed: int, total_nbs: int
):

    summary = "\n"
    nb_percent = int(float(n_passed) / float(total_nbs) * 100)
    summary += f"Notebooks: {n_passed} of {total_nbs} passed ({nb_percent}%)\n"
    total_cells = sum(map(lambda res: res.num_cells, notebook_results.values()))
    total_cells_passed = sum(
        map(lambda res: res.num_passing_cells, notebook_results.values())
    )
    percent = int(100.0 * float(total_cells_passed) / float(total_cells))
    summary += f"Cells: {total_cells_passed} of {total_cells} passed ({percent}%)\n"
    return summary
