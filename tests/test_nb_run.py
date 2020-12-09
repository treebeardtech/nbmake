import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml
from _pytest.pytester import Testdir
from jupyter_cache import get_cache
from jupyter_cache.cache.main import JupyterCacheBase

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

    def test_when_config_supplied_then_partially_overriden(
        self, testdir: Testdir, cache: JupyterCacheBase
    ):
        write_nb(passing_nb, filename)
        conf_path = write_config({"execute": {"timeout": 20}})
        run = NotebookRun(filename, path_output, cache, conf_path)

        real_check_output = subprocess.check_output
        with patch("subprocess.check_output") as check_output:
            check_output.side_effect = real_check_output
            run.execute()

            check_output.call_args

            jb_args = check_output.call_args[0][0]
            config_path = jb_args[jb_args.index("--config") + 1]
            config = yaml.load(Path(config_path).read_text())

            assert config["execute"]["timeout"] == 20
            assert config["execute"]["execute_notebooks"] == "force"
