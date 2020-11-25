import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import jupyter_book
from jupyter_cache import get_cache

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
    book_root: Path

    def __init__(
        self, book_root: str, filename: str, toc_filename: str, config_filename: str
    ) -> None:
        self.filename = Path(filename)
        self.book_root = Path(book_root)
        self.dirname = Path(os.path.dirname(self.filename))
        self.basename = Path(os.path.basename(self.filename))

        self.out_loc = self.book_root / f"_build/jupyter_execute/{self.basename}"

        toc, config = self.write_tmp_config(toc_filename, config_filename)
        self.toc_filename = toc
        self.config_filename = config

    def write_tmp_config(
        self, toc_filename: str, config_filename: str
    ) -> Tuple[Path, Path]:
        toc_tmp = Path(f"{tempfile.NamedTemporaryFile().name}.yml")
        config_tmp = Path(f"{tempfile.NamedTemporaryFile().name}.yml")
        shutil.copyfile(toc_filename, toc_tmp)
        shutil.copyfile(config_filename, config_tmp)
        return toc_tmp, config_tmp

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

    def rm_cache(self):
        cache = get_cache(self.book_root / "_build/.jupyter_cache")
        matches = [r for r in cache.list_cache_records() if r.uri == self.filename]

        if matches:
            cache.remove_cache(matches[0].pk)

    def execute(self) -> JupyterBookResult:
        self.rm_cache()

        workdir = Path(os.path.dirname(self.filename))
        out = subprocess.check_output(
            f"{JB_BINARY} build {self.book_root} --toc {self.toc_filename} --config {self.config_filename}",
            shell=True,
            cwd=workdir,
        )
        print(out.decode())
        doc = self._get_executed_ipynb(workdir)
        failing_cell_index = self._get_failing_cell_index(doc)
        return JupyterBookResult(document=doc, failing_cell_index=failing_cell_index)
