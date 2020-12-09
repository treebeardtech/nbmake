from __future__ import print_function

import os
from importlib import import_module, reload
from pathlib import Path

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


def test_when_in_build_dir_none_collected(testdir: Testdir):
    build_dir = Path("_build")
    build_dir.mkdir()
    write_nb(passing_nb, build_dir / "a.ipynb")

    items, hook_recorder = testdir.inline_genitems("--nbmake")

    assert hook_recorder.ret == ExitCode.NO_TESTS_COLLECTED
    assert len(items) == 0


def test_when_passing_nbs_then_ok(testdir: Testdir):
    nbs = [
        Path(testdir.tmpdir) / "a.ipynb",
        Path(testdir.tmpdir) / "b nb.ipynb",
        Path(testdir.tmpdir) / Path("sub dir/a.ipynb"),
        Path(testdir.tmpdir) / Path("sub dir/b.ipynb"),
    ]
    testdir.mkdir("sub dir")
    [write_nb(passing_nb, path) for path in nbs]

    hook_recorder = testdir.inline_run("--nbmake", "-vvv")

    assert hook_recorder.ret == ExitCode.OK


def test_when_run_from_non_root_then_ok(testdir: Testdir):
    nbs = [
        Path(testdir.tmpdir) / Path("sub dir/b.ipynb"),
    ]
    testdir.mkdir("sub dir")
    Path("pytest.ini").write_text("")
    os.chdir("sub dir")

    [write_nb(passing_nb, path) for path in nbs]

    hook_recorder = testdir.inline_run("--nbmake", "-vvv")

    assert hook_recorder.ret == ExitCode.OK


def test_when_failing_nb_then_fail(testdir: Testdir):
    write_nb(failing_nb, Path(testdir.tmpdir) / "a.ipynb")

    hook_recorder = testdir.inline_run("--nbmake", "-v")
    assert hook_recorder.ret == ExitCode.TESTS_FAILED


def test_when_html_flag_then_report(testdir: Testdir):
    write_nb(failing_nb, Path(testdir.tmpdir) / "a.ipynb")

    hook_recorder = testdir.inline_run("--nbmake", "--html")
    assert hook_recorder.ret == ExitCode.TESTS_FAILED
    assert Path("_build/html").exists()


def test_when_no_html_flag_then_no_build_dir(testdir: Testdir):
    write_nb(failing_nb, Path(testdir.tmpdir) / "a.ipynb")

    hook_recorder = testdir.inline_run("--nbmake")
    assert hook_recorder.ret == ExitCode.TESTS_FAILED
    assert not Path("_build").exists()


def test_when_path_output_then_build_dir(testdir: Testdir):
    write_nb(failing_nb, Path(testdir.tmpdir) / "a.ipynb")

    hook_recorder = testdir.inline_run("--nbmake", "--path-output=.")
    assert hook_recorder.ret == ExitCode.TESTS_FAILED
    assert Path("_build").exists()
