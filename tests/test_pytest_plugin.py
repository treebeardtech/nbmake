from __future__ import print_function

from pathlib import Path

import pytest
import yaml
from _pytest.pytester import Testdir
from pytest import ExitCode

from .helper import failing_nb, passing_nb, write_nb

pytest_plugins = "pytester"


def test_collection(testdir: Testdir):
    write_nb(passing_nb, Path(testdir.tmpdir) / "a.ipynb")

    items, hook_recorder = testdir.inline_genitems("--nbmake")

    assert hook_recorder.ret == ExitCode.OK  # type: ignore
    assert len(items) == 1


def test_when_ignored_none_collected(testdir: Testdir):
    write_nb(passing_nb, Path(testdir.tmpdir) / "a.ipynb")

    items, hook_recorder = testdir.inline_genitems(
        "--nbmake", "--ignore-glob", "*.ipynb"
    )

    assert hook_recorder.ret == ExitCode.NO_TESTS_COLLECTED  # type: ignore
    assert len(items) == 0


def test_when_config_passed_then_forwarded(testdir: Testdir):
    write_nb(passing_nb, Path(testdir.tmpdir) / "a.ipynb")

    config = "x.yml"
    with open(config, "w") as c:
        yaml.dump({"execute": {}}, c)

    hook_recorder = testdir.inline_run("--nbmake", f"--jbconfig={config}")

    assert hook_recorder.ret == ExitCode.OK  # type: ignore


def test_when_passing_nbs_then_ok(testdir: Testdir):
    write_nb(passing_nb, Path(testdir.tmpdir) / "a.ipynb", "a.ipynb")
    write_nb(passing_nb, Path(testdir.tmpdir) / "b.ipynb", "b.ipynb")
    testdir.mkdir("subdir")
    write_nb(
        ["import time;time.sleep(0)"],
        Path(testdir.tmpdir) / Path("subdir/a.ipynb"),
        "subdir/a.ipynb",
    )
    write_nb(
        passing_nb, Path(testdir.tmpdir) / Path("subdir/b.ipynb"), "subdir/b.ipynb"
    )

    hook_recorder = testdir.inline_run("--nbmake")

    assert hook_recorder.ret == ExitCode.OK  # type: ignore


@pytest.mark.xfail("")  # type: ignore
def test_when_parallel_passing_nbs_then_ok(testdir: Testdir):
    for i in range(10):
        write_nb(
            ["import time;time.sleep(1)"],
            Path(testdir.tmpdir) / f"{i}.ipynb",
        )

    hook_recorder = testdir.inline_run("--nbmake", "-n=4")

    assert hook_recorder.ret == ExitCode.OK  # type: ignore


def test_when_failing_nb_then_fail(testdir: Testdir):
    write_nb(failing_nb, Path(testdir.tmpdir) / "a.ipynb")

    hook_recorder = testdir.inline_run("--nbmake")
    assert hook_recorder.ret == ExitCode.TESTS_FAILED  # type: ignore
