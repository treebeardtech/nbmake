import os

from jupyter_cache import get_cache

from nbmake.jupyter_book_result import JupyterBookResult  # type: ignore
from nbmake.jupyter_book_run import JupyterBookRun  # type: ignore

# https://github.com/microsoft/pyright/issues/377



class TestJupyterBookRun:
    def test_passing(self):
        book_root = "tests/resources"
        filename = "passing.ipynb"
        toc = "tests/resources/_toc.yml"
        config = "tests/resources/_config.yml"
        cache = get_cache("tests/resources/_build/.jupyter_cache")

        run = JupyterBookRun(book_root, filename, toc, config)  # type: ignore
        res: JupyterBookResult = run.execute()  # type: ignore

        records = cache.list_cache_records()
        assert len(records) == 1
        matches = [r for r in records if r.uri == os.path.abspath(filename)]

        assert res.failing_cell_index == None

    def test_failing(self):
        filename = "tests/resources/failing.ipynb"
        run = JupyterBookRun(filename)  # type: ignore
        res: JupyterBookResult = run.execute()  # type: ignore

        assert res.failing_cell_index == 0
