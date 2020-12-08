from __future__ import print_function

from importlib import import_module, reload
from pathlib import Path

import yaml
from _pytest.pytester import Testdir
from pytest import ExitCode

from .helper import failing_nb, passing_nb, write_nb

pytest_plugins = "pytester"


def test_import():
    reload(import_module("nbmake.jupyter_book_adapter"))
    reload(import_module("nbmake.nb_result"))
    reload(import_module("nbmake.nb_run"))
    reload(import_module("nbmake.pytest_plugin"))
    reload(import_module("nbmake.pytest_items"))


def test_when_nb_present_then_collected(testdir: Testdir):
    write_nb(passing_nb, Path(testdir.tmpdir) / "a.ipynb")

    items, hook_recorder = testdir.inline_genitems("--nbmake")

    assert hook_recorder.ret == ExitCode.OK
    assert len(items) == 1


def test_when_ignored_none_collected(testdir: Testdir):
    write_nb(passing_nb, Path(testdir.tmpdir) / "a.ipynb")

    items, hook_recorder = testdir.inline_genitems(
        "--nbmake", "--ignore-glob", "*.ipynb"
    )

    assert hook_recorder.ret == ExitCode.NO_TESTS_COLLECTED
    assert len(items) == 0


def test_when_config_passed_then_forwarded(testdir: Testdir):
    write_nb(passing_nb, Path(testdir.tmpdir) / "a.ipynb")

    config = "x.yml"
    Path(config).write_text(yaml.dump({"execute": {}}))

    hook_recorder = testdir.inline_run("--nbmake", f"--jbconfig={config}")

    assert hook_recorder.ret == ExitCode.OK


def test_when_passing_nbs_then_ok(testdir: Testdir):
    nbs = [
        Path(testdir.tmpdir) / "a.ipynb",
        Path(testdir.tmpdir) / "b nb.ipynb",
        Path(testdir.tmpdir) / Path("sub dir/a.ipynb"),
        Path(testdir.tmpdir) / Path("sub dir/b.ipynb"),
    ]
    testdir.mkdir("sub dir")
    [write_nb(passing_nb, path) for path in nbs]

    hook_recorder = testdir.inline_run("--nbmake")

    assert hook_recorder.ret == ExitCode.OK


def test_when_failing_nb_then_fail(testdir: Testdir):
    write_nb(failing_nb, Path(testdir.tmpdir) / "a.ipynb")

    hook_recorder = testdir.inline_run("--nbmake")
    assert hook_recorder.ret == ExitCode.TESTS_FAILED
