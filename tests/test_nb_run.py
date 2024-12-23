from pathlib import Path

import pytest
from nbformat import write
from nbformat.v4 import new_code_cell, new_notebook, new_output
from typing_extensions import Never

from nbmake.nb_result import NotebookResult
from nbmake.nb_run import NotebookRun

from .helper import failing_nb, passing_nb, testdir2, write_nb

assert testdir2  # ensure testdir is not removed by linter

pytest_plugins = "pytester"

filename = Path("x.ipynb")


class TestNotebookRun:
    def test_when_passing_then_no_failing_cell(self, testdir2: Never):
        write_nb(passing_nb, filename)

        run = NotebookRun(filename, 300)
        res: NotebookResult = run.execute()

        assert res.error is None

    def test_when_runs_then_cwd_is_nb_location(self, testdir2: Never):
        subdir = Path("subdir")
        subdir.mkdir(exist_ok=True)
        write_nb(
            ["import os; assert os.getcwd().endswith('subdir')"], subdir / filename
        )

        run = NotebookRun(subdir / filename, 300)
        res: NotebookResult = run.execute()

        assert res.error is None

    def test_failing(self, testdir2: Never):
        write_nb(failing_nb, filename)
        run = NotebookRun(filename, 300)
        res: NotebookResult = run.execute()

        assert res.error and res.error.failing_cell_index == 1

    def test_when_allow_errors_then_passing(self, testdir2: Never):
        nb = new_notebook()
        nb.metadata.execution = {"allow_errors": True}
        cell = new_code_cell("raise Exception()")
        nb.cells.append(cell)
        write(nb, filename)

        run = NotebookRun(filename, 300)
        res: NotebookResult = run.execute()

        assert not res.error
        assert res.nb.cells[0].outputs[0].ename == "Exception"

    def test_when_timeout_then_fails(self, testdir2: Never):
        nb = new_notebook()
        nb.metadata.execution = {"timeout": 1}
        nb.cells += [
            new_code_cell("import time"),
            new_code_cell("time.sleep(2)"),
            new_code_cell("from pathlib import Path;Path('fail.txt').write_text('')"),
        ]
        write(nb, filename)

        run = NotebookRun(filename, 300)
        res: NotebookResult = run.execute()

        assert not Path("fail.txt").exists()
        assert res.error and res.error.failing_cell_index == 1

    def test_when_executed_then_stripped_out(self, testdir2: Never):
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

        run = NotebookRun(filename, 300)
        res: NotebookResult = run.execute()

        assert res.error and res.error.failing_cell_index == 0
        assert res.nb.cells[0].outputs[0].ename == "Exception"
        assert res.nb.cells[1].outputs == []

    def test_when_unknown_kernel_then_error(self, testdir2: Never):
        nb = new_notebook(
            metadata={"kernelspec": {"display_name": "asdf", "name": "asdf"}}
        )

        write(nb, filename)

        run = NotebookRun(filename, 300)
        res: NotebookResult = run.execute()
        assert res.error and "No such kernel" in res.error.summary

    def test_when_cell_ignored_then_does_not_run(self, testdir2: Never):
        nb = Path(__file__).parent / "resources" / "ignore_tag.ipynb"
        run = NotebookRun(nb, 300)
        res: NotebookResult = run.execute()
        assert res.error is None

    def test_when_raises_exc_tag_then_succeeds(self, testdir2: Never):
        nb = Path(__file__).parent / "resources" / "raises_tag.ipynb"
        run = NotebookRun(nb, 300)
        res: NotebookResult = run.execute()
        assert res.error is None

    def test_when_mock_then_succeeds(self, testdir2: Never):
        nb = Path(__file__).parent / "resources" / "mock.ipynb"
        run = NotebookRun(nb, 300)
        res: NotebookResult = run.execute()
        assert res.error is None

    def test_when_post_cell_execute_then_succeeds(self, testdir2: Never):
        nb = Path(__file__).parent / "resources" / "post_cell_execute.ipynb"
        run = NotebookRun(nb, 300)
        res: NotebookResult = run.execute()
        assert res.error is None

    def test_when_post_cell_execute_then_command_fails(self, testdir2: Never):
        nb = Path(__file__).parent / "resources" / "post_cell_execute_error.ipynb"
        run = NotebookRun(nb, 300)
        with pytest.raises(Exception) as exc_info:
            run.execute()

        assert exc_info is not None
        assert "boom!" in exc_info.value.args[0]

    def test_when_post_cell_execute_then_cell_fails(self, testdir2: Never):
        nb = (
            Path(__file__).parent / "resources" / "post_cell_execute_masked_error.ipynb"
        )
        run = NotebookRun(nb, 300)
        res: NotebookResult = run.execute()

        # make sure the cell exception (bang!) is raised and not masked
        # by the post cell execution exception (boom!)
        assert res.error is not None
        assert "bang!" in res.error.summary

    def test_when_magic_error_then_fails(self, testdir2: Never):
        nb = Path(__file__).parent / "resources" / "magic_error.ipynb"
        run = NotebookRun(nb, 300)
        res: NotebookResult = run.execute()
        assert res.error is not None

    def test_when_empty_then_succeeds(self, testdir2: Never):
        nb = Path(__file__).parent / "resources" / "empty.ipynb"
        run = NotebookRun(nb, 300)
        res: NotebookResult = run.execute()
        assert res.error is None

    def test_when_import_error_then_fails(self, testdir2: Never):
        nb = Path(__file__).parent / "resources" / "import_errs.ipynb"
        run = NotebookRun(nb, 1, find_import_errors=True)
        res: NotebookResult = run.execute()
        assert res.error is not None
        assert "ModuleNotFoundError" in res.error.summary
