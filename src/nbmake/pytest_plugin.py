import uuid
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, List, Optional

import yaml
from _pytest.config import Config, TerminalReporter  # type: ignore

from .pytest_items import NotebookFile
from .util import data_dir


def pytest_addoption(parser: Any):
    group = parser.getgroup("nbmake", "notebook testing")
    group.addoption("--nbmake", action="store_true", help="Test notebooks")
    group.addoption(
        "--jbconfig",
        action="store",
        help="Your jupyter-book config file",
    )
    group.addoption(
        "--path-output", action="store", default=str(data_dir / str(uuid.uuid4()))
    )
    # "--warningiserror",
    # "--nitpick",


def pytest_configure(config: Config):  # type: ignore
    # hack to prevent race condition initialising cache
    config_path = Path("_config.yml")
    path_out: str = config.option.path_output
    config_path.write_text(
        yaml.dump(
            {
                "exclude_patterns": [".*/**/*", "Library/**/*", ".pytest_cache/**/*"],
                "execute": {
                    "execute_notebooks": "cache",
                    "cache": str(Path(path_out) / "cache"),
                    # "only_build_toc_files": True
                },
            }
        )
    )


def pytest_collect_file(path: str, parent: Any) -> Optional[Any]:
    """
    Collect IPython notebooks using the specified pytest hook
    """
    opt = parent.config.option
    if opt.nbmake and fnmatch(path, "*.ipynb"):
        return NotebookFile.from_parent(parent, fspath=path)  # type: ignore

    return None


def pytest_collectreport(report: Any) -> None:
    """Collector finished collecting."""
    build_toc([Path(i.name) for i in report.result if isinstance(i, NotebookFile)])


def build_toc(files: List[Path]):
    toc = [{"file": str(f).replace(".ipynb", "")} for f in files]
    if len(toc) == 0:
        return
    toc[0]["title"] = "test results"
    toc_path = Path("_toc.yml")
    toc_path.write_text(yaml.dump(toc))


# def pytest_sessionfinish(session: Any, exitstatus: Any):
#     """ whole test run finishes. """


def pytest_terminal_summary(terminalreporter: TerminalReporter, exitstatus: int, config: Config):  # type: ignore
    toc_path = "_toc.yml"
    if not (getattr(config.option, "nbmake") and Path(toc_path).exists()):  # type: ignore
        return

    import subprocess
    from subprocess import CalledProcessError

    from .jupyter_book_run import JB_BINARY

    config_path = "_config.yml"
    path_output: str = config.option.path_output
    args = [
        str(JB_BINARY),
        "build",
        f"--toc={toc_path}",
        f"--config={config_path}",
        f"--path-output={path_output}",
        str(config.rootdir),  # type: ignore
    ]
    try:
        out = subprocess.check_output(args, stderr=subprocess.STDOUT)
        (Path(path_output) / "nbmake.log").write_bytes(out)

        url = (
            f"  file://{Path(path_output).absolute().as_posix()}/_build/html/index.html"
        )
        terminalreporter.line(f"\n\nBuilt test report (Open in browser).\n\n{url}\n")
    except CalledProcessError as err:
        terminalreporter.line(
            f"Nbmake failed to build test report with command\n{' '.join(args)}"
        )
        terminalreporter.line(err.output.decode())
