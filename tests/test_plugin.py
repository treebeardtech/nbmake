# type: ignore
from __future__ import print_function

import os

import nbformat
from _pytest.pytester import Testdir
from pytest import ExitCode

pytest_plugins = "pytester"


def _build_nb(sources):
    """Builds a notebook of only code cells, from a list of sources"""
    nb = nbformat.v4.new_notebook()
    for src in sources:
        nb.cells.append(nbformat.v4.new_code_cell(src))
    return nb


def _write_nb(sources, path):
    nb = _build_nb(sources)
    nbformat.write(nb, path)


passing_nb = [
    # In [1]:
    "a = 5",
    # In [2]:
    "for i in range(10):\n" + "    print(i)",
    # In [3]:
    "print(a)",
    # In [4]:
    "a",
    # In [5]:
    "import os\n" + "os.curdir",
]

failing_nb = [
    # In [1]:
    "raise Exception()"
]


def test_collection(testdir: Testdir):
    _write_nb(passing_nb, os.path.join(str(testdir.tmpdir), "test_collection.ipynb"))

    items, _ = testdir.inline_genitems("--treebeard")

    assert len(items) == 1


def test_when_ignored_none_collected(testdir: Testdir):
    _write_nb(passing_nb, os.path.join(str(testdir.tmpdir), "test_collection.ipynb"))

    items, _ = testdir.inline_genitems("--treebeard --ignore **/*ipynb")

    assert len(items) == 0


def test_when_passing_nbs_then_ok(testdir: Testdir):
    _write_nb(passing_nb, os.path.join(str(testdir.tmpdir), "test_collection.ipynb"))
    testdir.mkdir("subdir")
    _write_nb(
        passing_nb, os.path.join(str(testdir.tmpdir), "subdir/test_collection.ipynb")
    )
    _write_nb(
        passing_nb, os.path.join(str(testdir.tmpdir), "subdir/test_collection2.ipynb")
    )

    hook_recorder = testdir.inline_run("--treebeard")

    assert hook_recorder.ret == ExitCode.OK


def test_when_failing_nb_then_fail(testdir: Testdir):
    _write_nb(failing_nb, os.path.join(str(testdir.tmpdir), "test_collection.ipynb"))

    hook_recorder = testdir.inline_run("--treebeard")

    assert hook_recorder.ret == ExitCode.TESTS_FAILED
