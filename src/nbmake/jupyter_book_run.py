import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

import jupyter_book

from .jupyter_book_result import JupyterBookResult

JB_BINARY: Path = (
    Path(os.path.dirname(jupyter_book.__file__))
    / ("../../../Scripts/jb.exe" if os.name == "nt" else "../../../../bin/jb")
).resolve()


class JupyterBookRun:
    filename: Path
    dirname: Path
    basename: Path
    out_loc: Path

    def __init__(self, filename: str) -> None:
        self.filename = Path(filename)
        self.dirname = Path(os.path.dirname(self.filename))
        self.basename = Path(os.path.basename(self.filename))

        page_name = str(self.basename).replace(".ipynb", "")
        self.out_loc = Path(
            f".nbmake/_build/_page/{page_name}/jupyter_execute/{self.basename}"
        )

    def _get_executed_ipynb(self, workdir: Path) -> Dict[Any, Any]:

        with open(workdir / self.out_loc) as j:
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

    def execute(self) -> JupyterBookResult:
        workdir = Path(os.path.dirname(self.filename))
        shutil.rmtree(workdir / ".nbmake", ignore_errors=True)
        out = subprocess.check_output(
            f"{JB_BINARY} build {os.path.basename(self.filename)} --path-output .nbmake",
            shell=True,
            cwd=workdir,
        )
        print(out.decode())
        doc = self._get_executed_ipynb(workdir)
        failing_cell_index = self._get_failing_cell_index(doc)
        return JupyterBookResult(document=doc, failing_cell_index=failing_cell_index)
