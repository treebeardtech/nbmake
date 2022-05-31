from __future__ import print_function

import os
from importlib import import_module, reload
from pathlib import Path

from _pytest.pytester import Testdir
from nbformat import read
from pytest import ExitCode

from .helper import failing_nb, passing_nb, testdir2, write_nb

pytest_plugins = "pytester"
NB_VERSION = 4


def test_import():
    reload(import_module("nbmake.nb_result"))
    reload(import_module("nbmake.nb_run"))
    reload(import_module("nbmake.pytest_plugin"))
    reload(import_module("nbmake.pytest_items"))


def test_when_nb_present_then_collected(testdir2: Testdir):
    write_nb(passing_nb, Path(testdir2.tmpdir) / "a.ipynb")

    items, hook_recorder = testdir2.inline_genitems("--nbmake")

    assert hook_recorder.ret == ExitCode.OK
    assert len(items) == 1


def test_when_ignored_none_collected(testdir2: Testdir):
    write_nb(passing_nb, Path(testdir2.tmpdir) / "a.ipynb")

    items, hook_recorder = testdir2.inline_genitems(
        "--nbmake", "--ignore-glob", "*.ipynb"
    )

    assert hook_recorder.ret == ExitCode.NO_TESTS_COLLECTED
    assert len(items) == 0


def test_when_in_build_dir_none_collected(testdir2: Testdir):
    build_dir = Path("_build")
    build_dir.mkdir()
    write_nb(passing_nb, build_dir / "a.ipynb")

    items, hook_recorder = testdir2.inline_genitems("--nbmake")

    assert hook_recorder.ret == ExitCode.NO_TESTS_COLLECTED
    assert len(items) == 0


def test_when_parallel_passing_nbs_then_ok(testdir2: Testdir):
    [write_nb(passing_nb, Path(f"{i}.ipynb")) for i in range(20)]

    hook_recorder = testdir2.inline_run("--nbmake", "-n=auto")

    assert hook_recorder.ret == ExitCode.OK


def test_when_passing_nbs_then_ok(testdir2: Testdir):
    nbs = [
        Path(testdir2.tmpdir) / "a.ipynb",
        Path(testdir2.tmpdir) / "b nb.ipynb",
        Path(testdir2.tmpdir) / Path("sub dir/a.ipynb"),
        Path(testdir2.tmpdir) / Path("sub dir/b.ipynb"),
    ]
    testdir2.mkdir("sub dir")
    [write_nb(passing_nb, path) for path in nbs]

    hook_recorder = testdir2.inline_run("--nbmake", "-vvv")

    for path in nbs:
        nb = read(str(path), NB_VERSION)
        for cell in nb.cells:
            if "outputs" in cell:
                assert cell.outputs == []

    assert hook_recorder.ret == ExitCode.OK


def test_when_overwrite_then_overwritten(testdir2: Testdir):
    nbs = [
        Path(testdir2.tmpdir) / Path("sub dir/b.ipynb"),
    ]
    testdir2.mkdir("sub dir")
    [write_nb(["1+1"], path) for path in nbs]

    hook_recorder = testdir2.inline_run("--nbmake", "--overwrite")

    for path in nbs:
        nb = read(str(path), NB_VERSION)
        for cell in nb.cells:
            if "outputs" in cell:
                assert cell.outputs != []

    assert hook_recorder.ret == ExitCode.OK


def test_when_run_from_non_root_then_ok(testdir2: Testdir):
    nbs = [
        Path(testdir2.tmpdir) / Path("sub dir/b.ipynb"),
    ]
    testdir2.mkdir("sub dir")
    Path("pytest.ini").write_text("")
    os.chdir("sub dir")

    [write_nb(passing_nb, path) for path in nbs]

    hook_recorder = testdir2.inline_run("--nbmake", "-vvv")

    assert hook_recorder.ret == ExitCode.OK


def test_when_failing_nb_then_fail(testdir2: Testdir):
    write_nb(failing_nb, Path(testdir2.tmpdir) / "a.ipynb")

    hook_recorder = testdir2.inline_run("--nbmake", "-v")
    assert hook_recorder.ret == ExitCode.TESTS_FAILED


def test_when_no_html_flag_then_no_build_dir(testdir2: Testdir):
    write_nb(failing_nb, Path(testdir2.tmpdir) / "a.ipynb")

    hook_recorder = testdir2.inline_run("--nbmake")
    assert hook_recorder.ret == ExitCode.TESTS_FAILED
    assert not Path("_build").exists()


def test_when_init_then_passes(testdir2: Testdir):
    example_dir = Path(testdir2.tmpdir) / "example"
    example_dir.mkdir()
    write_nb(passing_nb, example_dir / "a.ipynb")
    (example_dir / "__init__.py").write_text("")

    hook_recorder = testdir2.inline_run("--nbmake")

    assert hook_recorder.ret == ExitCode.OK


def test_when_timeout_flag_then_uses_as_default(testdir2: Testdir):
    example_dir = Path(testdir2.tmpdir) / "example"
    example_dir.mkdir()
    write_nb(["import time; time.sleep(2)"], example_dir / "a.ipynb")

    hook_recorder = testdir2.inline_run("--nbmake", "--nbmake-timeout=3")
    assert hook_recorder.ret == ExitCode.OK

    hook_recorder = testdir2.inline_run("--nbmake", "--nbmake-timeout=1")
    assert hook_recorder.ret == ExitCode.TESTS_FAILED


def test_when_explicit_metadata_then_ignore_timeout(testdir2: Testdir):
    example_dir = Path(testdir2.tmpdir) / "example"
    example_dir.mkdir()
    write_nb(
        ["import time; time.sleep(2)"],
        example_dir / "a.ipynb",
        metadata={"execution": {"timeout": 10}},
    )

    hook_recorder = testdir2.inline_run("--nbmake", "--nbmake-timeout=1")
    assert hook_recorder.ret == ExitCode.OK


def test_when_kernel_passed_then_override(testdir2: Testdir):
    write_nb(
        passing_nb,
        Path(f"x.ipynb"),
        metadata={
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "blah",
            }
        },
    )

    hook_recorder = testdir2.inline_run("--nbmake", "--nbmake-kernel=python3")

    assert hook_recorder.ret == ExitCode.OK
