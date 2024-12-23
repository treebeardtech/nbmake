from __future__ import print_function

import os
from importlib import import_module, reload
from pathlib import Path

from nbformat import read
from pytest import ExitCode, Pytester
from typing_extensions import Never

from .helper import failing_nb, passing_nb, testdir2, write_nb

assert testdir2  # ensure testdir is not removed by linter

pytest_plugins = "pytester"
NB_VERSION = 4


def test_import():
    reload(import_module("nbmake.nb_result"))
    reload(import_module("nbmake.nb_run"))
    reload(import_module("nbmake.pytest_plugin"))
    reload(import_module("nbmake.pytest_items"))


def test_when_nb_present_then_collected(pytester: Pytester, testdir2: Never):
    write_nb(passing_nb, Path(pytester.path) / "a.ipynb")

    items, hook_recorder = pytester.inline_genitems("--nbmake")

    assert hook_recorder.ret == ExitCode.OK
    assert len(items) == 1


def test_when_ignored_none_collected(pytester: Pytester, testdir2: Never):
    write_nb(passing_nb, Path(pytester.path) / "a.ipynb")

    items, hook_recorder = pytester.inline_genitems(
        "--nbmake", "--ignore-glob", "*.ipynb"
    )

    assert hook_recorder.ret == ExitCode.NO_TESTS_COLLECTED
    assert len(items) == 0


def test_when_in_build_dir_none_collected(pytester: Pytester, testdir2: Never):
    build_dir = Path("_build")
    build_dir.mkdir()
    write_nb(passing_nb, build_dir / "a.ipynb")

    items, hook_recorder = pytester.inline_genitems("--nbmake")

    assert hook_recorder.ret == ExitCode.NO_TESTS_COLLECTED
    assert len(items) == 0


def test_when_parallel_passing_nbs_then_ok(pytester: Pytester, testdir2: Never):
    [write_nb(passing_nb, Path(f"{i}.ipynb")) for i in range(20)]

    hook_recorder = pytester.inline_run("--nbmake", "-n=auto")

    assert hook_recorder.ret == ExitCode.OK


def test_when_passing_nbs_then_ok(pytester: Pytester, testdir2: Never):
    nbs = [
        Path(pytester.path) / "a.ipynb",
        Path(pytester.path) / "b nb.ipynb",
        Path(pytester.path) / Path("sub dir/a.ipynb"),
        Path(pytester.path) / Path("sub dir/b.ipynb"),
    ]
    pytester.mkdir("sub dir")
    [write_nb(passing_nb, path) for path in nbs]

    hook_recorder = pytester.inline_run("--nbmake", "-vvv")

    for path in nbs:
        nb = read(str(path), NB_VERSION)
        for cell in nb.cells:
            if "outputs" in cell:
                assert cell.outputs == []

    assert hook_recorder.ret == ExitCode.OK


def test_when_overwrite_then_overwritten(pytester: Pytester, testdir2: Never):
    nbs = [
        Path(pytester.path) / Path("sub dir/b.ipynb"),
    ]
    pytester.mkdir("sub dir")
    [write_nb(["1+1"], path) for path in nbs]

    hook_recorder = pytester.inline_run("--nbmake", "--overwrite")

    for path in nbs:
        nb = read(str(path), NB_VERSION)
        for cell in nb.cells:
            if "outputs" in cell:
                assert cell.outputs != []

    assert hook_recorder.ret == ExitCode.OK


def test_when_run_from_non_root_then_ok(pytester: Pytester, testdir2: Never):
    os.environ["PATH"] += f"/home/vscode:{os.environ['PATH']}"
    nbs = [
        Path(pytester.path) / Path("sub dir/b.ipynb"),
    ]
    pytester.mkdir("sub dir")
    Path("pytest.ini").write_text("")
    os.chdir("sub dir")

    [write_nb(passing_nb, path) for path in nbs]

    hook_recorder = pytester.inline_run("--nbmake", "-vvv")

    assert hook_recorder.ret == ExitCode.OK


def test_when_failing_nb_then_fail(pytester: Pytester, testdir2: Never):
    write_nb(failing_nb, Path(pytester.path) / "a.ipynb")

    hook_recorder = pytester.inline_run("--nbmake", "-v")
    assert hook_recorder.ret == ExitCode.TESTS_FAILED


def test_when_no_html_flag_then_no_build_dir(pytester: Pytester, testdir2: Never):
    write_nb(failing_nb, Path(pytester.path) / "a.ipynb")

    hook_recorder = pytester.inline_run("--nbmake")
    assert hook_recorder.ret == ExitCode.TESTS_FAILED
    assert not Path("_build").exists()


def test_when_init_then_passes(pytester: Pytester, testdir2: Never):
    example_dir = Path(pytester.path) / "example"
    example_dir.mkdir()
    write_nb(passing_nb, example_dir / "a.ipynb")
    (example_dir / "__init__.py").write_text("")

    hook_recorder = pytester.inline_run("--nbmake")

    assert hook_recorder.ret == ExitCode.OK


def test_when_timeout_flag_then_uses_as_default(pytester: Pytester, testdir2: Never):
    example_dir = Path(pytester.path) / "example"
    example_dir.mkdir()
    write_nb(["import time; time.sleep(2)"], example_dir / "a.ipynb")

    hook_recorder = pytester.inline_run("--nbmake", "--nbmake-timeout=3")
    assert hook_recorder.ret == ExitCode.OK

    hook_recorder = pytester.inline_run("--nbmake", "--nbmake-timeout=1")
    assert hook_recorder.ret == ExitCode.TESTS_FAILED


def test_when_explicit_metadata_then_ignore_timeout(
    pytester: Pytester, testdir2: Never
):
    example_dir = Path(pytester.path) / "example"
    example_dir.mkdir()
    write_nb(
        ["import time; time.sleep(2)"],
        example_dir / "a.ipynb",
        metadata={"execution": {"timeout": 10}},
    )

    hook_recorder = pytester.inline_run("--nbmake", "--nbmake-timeout=1")
    assert hook_recorder.ret == ExitCode.OK


def test_when_kernel_passed_then_override(pytester: Pytester, testdir2: Never):
    write_nb(
        passing_nb,
        Path("x.ipynb"),
        metadata={
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "blah",
            }
        },
    )

    hook_recorder = pytester.inline_run("--nbmake", "--nbmake-kernel=python3")

    assert hook_recorder.ret == ExitCode.OK


def test_when_no_import_errs_then_pass(pytester: Pytester, testdir2: Never):
    write_nb(
        ["import itertools", "1/0", "import pickle"],
        Path(pytester.path) / "a.ipynb",
    )

    hook_recorder = pytester.inline_run("--nbmake", "--nbmake-find-import-errors")

    assert hook_recorder.ret == ExitCode.OK


def test_when_not_json_then_correct_err_msg(pytester: Pytester, testdir2: Never):
    (Path(pytester.path) / "a.ipynb").write_text("invalid json")

    hook_recorder = pytester.inline_run("--nbmake")

    longrepr = hook_recorder.listoutcomes()[2][0].longrepr
    assert longrepr is not None
    assert "NBMAKE INTERNAL ERROR" not in longrepr.term
    assert "json" in longrepr.term
