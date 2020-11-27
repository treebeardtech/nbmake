from __future__ import print_function

import os
from pathlib import Path

import yaml
from _pytest.pytester import Testdir  # type: ignore
from .helper import failing_nb, passing_nb, write_nb  # type: ignore
from pytest import ExitCode  # type: ignore

pytest_plugins = "pytester"


def test_collection(testdir: Testdir):  # type: ignore
    write_nb(passing_nb, os.path.join(str(testdir.tmpdir), "a.ipynb"))  # type: ignore

    items, _ = testdir.inline_genitems("--nbmake")  # type: ignore

    assert len(items) == 1  # type: ignore


def test_when_ignored_none_collected(testdir: Testdir):  # type: ignore
    write_nb(passing_nb, os.path.join(str(testdir.tmpdir), "a.ipynb"))  # type: ignore

    items, _ = testdir.inline_genitems("--nbmake --ignore **/*ipynb")  # type: ignore

    assert len(items) == 0  # type: ignore


def test_when_config_passed_then_forwarded(testdir: Testdir):  # type: ignore
    write_nb(passing_nb, os.path.join(str(testdir.tmpdir), "a.ipynb"))  # type: ignore

    config = "x.yml"
    with open(config, "w") as c:
        yaml.dump({"execute": {}}, c)

    hook_recorder = testdir.inline_run("--nbmake", f"--jbconfig={config}")  # type: ignore

    assert hook_recorder.ret == ExitCode.OK


def test_when_passing_nbs_then_ok(testdir: Testdir):  # type: ignore
    write_nb(passing_nb, os.path.join(str(testdir.tmpdir), "a.ipynb"))  # type: ignore
    testdir.mkdir("subdir")
    write_nb(
        ["import time;time.sleep(5)"],
        os.path.join(str(testdir.tmpdir), Path("subdir/a.ipynb")),  # type: ignore
    )
    write_nb(
        passing_nb,
        os.path.join(str(testdir.tmpdir), Path("subdir/b.ipynb")),  # type: ignore
    )

    hook_recorder = testdir.inline_run("--nbmake")  # type: ignore

    assert hook_recorder.ret == ExitCode.OK


def test_when_parallel_passing_nbs_then_ok(testdir: Testdir):  # type: ignore
    for i in range(10):
        write_nb(
            ["import time;time.sleep(3)"],
            os.path.join(str(testdir.tmpdir), f"{i}.ipynb"),  # type: ignore
        )

    hook_recorder = testdir.inline_run("--nbmake", "-n=4")  # type: ignore

    assert hook_recorder.ret == ExitCode.OK


def test_when_failing_nb_then_fail(testdir: Testdir):  # type: ignore
    write_nb(failing_nb, os.path.join(str(testdir.tmpdir), "test_collection.ipynb"))  # type: ignore

    hook_recorder = testdir.inline_run("--nbmake")  # type: ignore

    assert hook_recorder.ret == ExitCode.TESTS_FAILED
