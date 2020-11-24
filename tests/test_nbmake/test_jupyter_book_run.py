from nbmake.jupyter_book_result import JupyterBookResult  # type: ignore
from nbmake.jupyter_book_run import JupyterBookRun  # type: ignore

# https://github.com/microsoft/pyright/issues/377


class TestJupyterBookRun:
    def test_passing(self):
        filename = "tests/resources/passing.ipynb"
        run = JupyterBookRun(filename)  # type: ignore
        res: JupyterBookResult = run.execute()  # type: ignore

        assert res.failing_cell_index == None

    def test_failing(self):
        filename = "tests/resources/failing.ipynb"
        run = JupyterBookRun(filename)  # type: ignore
        res: JupyterBookResult = run.execute()  # type: ignore

        assert res.failing_cell_index == 0
