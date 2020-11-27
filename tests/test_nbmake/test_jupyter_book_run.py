import os
from pathlib import Path

from _pytest.pytester import Testdir
from helper import write_nb
from jupyter_cache import get_cache  # type: ignore

from nbmake.jupyter_book_result import JupyterBookResult  # type: ignore
from nbmake.jupyter_book_run import JupyterBookRun  # type: ignore

pytest_plugins = "pytester"
# https://github.com/microsoft/pyright/issues/377


class TestJupyterBookRun:
    def test_when_passing_then_no_failing_cell(self, testdir: Testdir):
        file = "p.ipynb"
        write_nb(["print hello"], file)

        run = JupyterBookRun(file)  # type: ignore
        res: JupyterBookResult = run.execute()  # type: ignore

        assert res.failing_cell_index == None

    def test_when_passing_and_config_then_cache_populated(self):
        filename = Path(os.path.abspath("tests/resources/passing.ipynb"))
        config = Path(os.path.abspath("tests/resources/_config.yml"))

        run = JupyterBookRun(filename, config)  # type: ignore
        res: JupyterBookResult = run.execute()  # type: ignore

        assert res.failing_cell_index == None

        cache = get_cache("tests/resources/_build/.jupyter_cache")  # type: ignore
        records = cache.list_cache_records()  # type: ignore
        assert len(records) == 1  # type: ignore
        assert records[0].uri == os.path.abspath(filename)  # type: ignore

    def test_failing(self):
        filename = "tests/resources/failing.ipynb"
        run = JupyterBookRun(filename)  # type: ignore
        res: JupyterBookResult = run.execute()  # type: ignore

        assert res.failing_cell_index == 0
