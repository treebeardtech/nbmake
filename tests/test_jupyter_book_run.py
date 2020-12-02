import os
import subprocess
from unittest.mock import patch

import yaml
from _pytest.pytester import Testdir
from jupyter_cache import get_cache  # type: ignore

from nbmake.jupyter_book_result import JupyterBookResult  # type: ignore
from nbmake.jupyter_book_run import JupyterBookRun  # type: ignore

from .helper import failing_nb, passing_nb, write_config, write_nb

pytest_plugins = "pytester"

filename = "x.ipynb"


class TestJupyterBookRun:
    def test_when_passing_then_no_failing_cell(self, testdir: Testdir):
        write_nb(passing_nb, filename)

        run = JupyterBookRun(filename)  # type: ignore
        res: JupyterBookResult = run.execute()  # type: ignore

        assert res.error == None

    def test_when_passing_and_config_then_cache_populated(self, testdir: Testdir):
        write_nb(passing_nb, filename)
        conf_path = write_config({"title": "blah"})

        run = JupyterBookRun(filename, conf_path)  # type: ignore
        res: JupyterBookResult = run.execute()  # type: ignore

        assert res.error == None

        cache = get_cache("_build/.jupyter_cache")  # type: ignore
        records = cache.list_cache_records()  # type: ignore
        assert len(records) == 1  # type: ignore
        assert records[0].uri == os.path.abspath(filename)  # type: ignore

    def test_failing(self, testdir: Testdir):
        write_nb(failing_nb, filename)
        run = JupyterBookRun(filename)  # type: ignore
        res: JupyterBookResult = run.execute()  # type: ignore

        assert res.error and res.error.failing_cell_index == 0  # type: ignore

    def test_when_config_supplied_then_partially_overriden(self, testdir: Testdir):
        write_nb(passing_nb, filename)
        conf_path = write_config({"execute": {"timeout": 20}})
        run = JupyterBookRun(filename, conf_path)  # type: ignore

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
                assert config["execute"]["execute_notebooks"] == "cache"
                assert config["execute"]["cache"] != None

            run.execute()
