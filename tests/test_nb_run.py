from pathlib import Path

import pytest
from _pytest.pytester import Testdir
from jupyter_cache import get_cache
from jupyter_cache.cache.main import JupyterCacheBase
from nbformat import write
from nbformat.v4 import new_code_cell, new_notebook, new_output

NB_VERSION = 4
from nbmake.nb_result import NotebookResult
from nbmake.nb_run import NotebookRun

from .helper import failing_nb, passing_nb, write_nb

pytest_plugins = "pytester"

filename = Path("x.ipynb")

path_output = Path("_build")


@pytest.fixture
def cache(request) -> JupyterCacheBase:
    return get_cache(path_output / request.node.name / "_build" / ".jupyter_cache")


class TestNotebookRun:
    def test_when_passing_then_no_failing_cell(self, testdir: Testdir):
        write_nb(passing_nb, filename)

        run = NotebookRun(filename)
        res: NotebookResult = run.execute()

        assert res.error == None

    def test_when_runs_then_cwd_is_nb_location(self, testdir: Testdir):
        subdir = Path("subdir")
        subdir.mkdir()
        write_nb(
            ["import os; assert os.getcwd().endswith('subdir')"], subdir / filename
        )

        run = NotebookRun(subdir / filename)
        res: NotebookResult = run.execute()

        assert res.error == None

    def test_failing(self, testdir: Testdir):
        write_nb(failing_nb, filename)
        run = NotebookRun(filename)
        res: NotebookResult = run.execute()

        assert res.error and res.error.failing_cell_index == 1

    def test_when_allow_errors_then_passing(self, testdir: Testdir):
        nb = new_notebook()
        nb.metadata.execution = {"allow_errors": True}
        cell = new_code_cell("raise Exception()")
        nb.cells.append(cell)
        write(nb, filename)

        run = NotebookRun(filename)
        res: NotebookResult = run.execute()

        assert not res.error
        assert res.nb.cells[0].outputs[0].ename == "Exception"

    def test_when_timeout_then_fails(self, testdir: Testdir):
        nb = new_notebook()
        nb.metadata.execution = {"timeout": 1}
        nb.cells += [
            new_code_cell("import time"),
            new_code_cell("time.sleep(2)"),
            new_code_cell("from pathlib import Path;Path('fail.txt').write_text('')"),
        ]
        write(nb, filename)

        run = NotebookRun(filename)
        res: NotebookResult = run.execute()

        assert not Path("fail.txt").exists()
        assert res.error and res.error.failing_cell_index == 1

    def test_when_executed_then_stripped_out(self, testdir: Testdir):
        nb = new_notebook(metadata={})
        nb.cells += [
            new_code_cell(
                ["raise Exception()"], metadata={}, outputs=[new_output("error")]
            ),
            new_code_cell(
                ["raise Exception()"], metadata={}, outputs=[new_output("error")]
            ),
        ]
        write(nb, filename)

        run = NotebookRun(filename)
        res: NotebookResult = run.execute()

        assert res.error and res.error.failing_cell_index == 0
        assert res.nb.cells[0].outputs[0].ename == "Exception"
        assert res.nb.cells[1].outputs == []
