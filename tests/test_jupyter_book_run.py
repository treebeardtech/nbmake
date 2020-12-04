import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml
from _pytest.pytester import Testdir
from jupyter_cache import get_cache  # type: ignore
from jupyter_cache.cache.main import JupyterCacheBase  # type: ignore

from nbmake.jupyter_book_result import JupyterBookResult  # type: ignore
from nbmake.jupyter_book_run import JupyterBookRun  # type: ignore

from .helper import failing_nb, passing_nb, write_config, write_nb

pytest_plugins = "pytester"

filename = Path("x.ipynb")

path_output = Path("_build")


@pytest.fixture  # type: ignore
def cache(request) -> JupyterCacheBase:  # type: ignore
    return get_cache(path_output / request.node.name / "cache")  # type: ignore


class TestJupyterBookRun:
    def test_when_passing_then_no_failing_cell(self, testdir: Testdir, cache: JupyterCacheBase):  # type: ignore
        write_nb(passing_nb, filename)

        run = JupyterBookRun(filename, path_output, cache)  # type: ignore
        res: JupyterBookResult = run.execute()  # type: ignore

        assert res.error == None

    def test_when_passing_then_cache_populated(self, testdir: Testdir, cache: JupyterCacheBase):  # type: ignore
        write_nb(passing_nb, filename)

        run = JupyterBookRun(filename, path_output, cache)  # type: ignore
        res: JupyterBookResult = run.execute()  # type: ignore

        assert res.error == None

        records = run.cache.list_cache_records()  # type: ignore
        assert len(records) == 1  # type: ignore
        assert records[0].uri.endswith(str(filename))  # type: ignore

    def test_when_failing_then_cache_populated(self, testdir: Testdir, cache: JupyterCacheBase):  # type: ignore
        write_nb(failing_nb, filename)
        # conf_path = write_config({"title": "blah"})

        run = JupyterBookRun(filename, path_output, cache)  # type: ignore
        res: JupyterBookResult = run.execute()  # type: ignore

        assert res.error

        records = run.cache.list_cache_records()  # type: ignore
        assert len(records) == 1  # type: ignore
        assert records[0].uri.endswith(str(filename))  # type: ignore

    def test_failing(self, testdir: Testdir, cache: JupyterCacheBase):  # type: ignore
        write_nb(failing_nb, filename)
        run = JupyterBookRun(filename, path_output, cache)  # type: ignore
        res: JupyterBookResult = run.execute()  # type: ignore

        assert res.error and res.error.failing_cell_index == 1  # type: ignore

    def test_when_config_supplied_then_partially_overriden(
        self, testdir: Testdir, cache: JupyterCacheBase  # type: ignore
    ):
        write_nb(passing_nb, filename)
        conf_path = write_config({"execute": {"timeout": 20}})
        run = JupyterBookRun(filename, path_output, cache, conf_path)  # type: ignore

        real_check_output = subprocess.check_output
        with patch("subprocess.check_output") as check_output:
            check_output.side_effect = real_check_output
            run.execute()

            check_output.call_args

            jb_args = check_output.call_args[0][0]
            config_path = jb_args[jb_args.index("--config") + 1]
            with open(config_path, "r") as c:
                config = yaml.load(c)

                assert config["execute"]["timeout"] == 20
                assert config["execute"]["execute_notebooks"] == "force"
