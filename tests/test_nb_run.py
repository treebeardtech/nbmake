import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml
from _pytest.pytester import Testdir
from jupyter_cache import get_cache
from jupyter_cache.cache.main import JupyterCacheBase
from nbformat import write
from nbformat.v4 import new_code_cell, new_notebook

from nbmake.nb_result import NotebookResult
from nbmake.nb_run import NotebookRun

from .helper import failing_nb, passing_nb, write_config, write_nb

pytest_plugins = "pytester"

filename = Path("x.ipynb")

path_output = Path("_build")


@pytest.fixture
def cache(request) -> JupyterCacheBase:
    return get_cache(path_output / request.node.name / "_build" / ".jupyter_cache")


class TestNotebookRun:
    def test_when_passing_then_no_failing_cell(
        self, testdir: Testdir, cache: JupyterCacheBase
    ):
        write_nb(passing_nb, filename)

        run = NotebookRun(filename, path_output, cache)
        res: NotebookResult = run.execute()

        assert res.error == None

    def test_when_passing_then_cache_populated(
        self, testdir: Testdir, cache: JupyterCacheBase
    ):
        write_nb(passing_nb, filename)

        run = NotebookRun(filename, path_output, cache)
        res: NotebookResult = run.execute()

        assert res.error == None

        records = run.cache.list_cache_records()
        assert len(records) == 1
        assert records[0].uri.endswith(str(filename))

    def test_when_failing_then_cache_populated(
        self, testdir: Testdir, cache: JupyterCacheBase
    ):
        write_nb(failing_nb, filename)

        run = NotebookRun(filename, path_output, cache)
        res: NotebookResult = run.execute()

        assert res.error

        records = run.cache.list_cache_records()
        assert len(records) == 1
        assert records[0].uri.endswith(str(filename))

    def test_failing(self, testdir: Testdir, cache: JupyterCacheBase):
        write_nb(failing_nb, filename)
        run = NotebookRun(filename, path_output, cache)
        res: NotebookResult = run.execute()

        assert res.error and res.error.failing_cell_index == 1

    def test_when_allow_errors_then_passing(
        self, testdir: Testdir, cache: JupyterCacheBase
    ):
        nb = new_notebook()
        nb.metadata.execution = {"allow_errors": True}
        cell = new_code_cell("raise Exception()")
        nb.cells.append(cell)
        write(nb, filename)

        run = NotebookRun(filename, path_output, cache)
        res: NotebookResult = run.execute()

        assert not res.error
        assert res.nb.cells[0].outputs[0].ename == "Exception"

    def test_when_timeout_then_fails(self, testdir: Testdir, cache: JupyterCacheBase):
        nb = new_notebook()
        nb.metadata.execution = {"timeout": 1}
        nb.cells += [new_code_cell("import time"), new_code_cell("time.sleep(2)")]
        write(nb, filename)

        run = NotebookRun(filename, path_output, cache)
        res: NotebookResult = run.execute()

        assert res.error and res.error.failing_cell_index == 1
