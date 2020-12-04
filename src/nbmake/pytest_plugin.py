import uuid
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, List, Optional

import yaml
from _pytest.config import Config  # type: ignore
from jupyter_cache import get_cache  # type: ignore
from jupyter_cache.cache.main import JupyterCacheBase  # type: ignore

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


def pytest_terminal_summary(terminalreporter: Any, exitstatus: int, config: Config):  # type: ignore
    option: Any = config.option
    toc_path = "_toc.yml"
    if not hasattr(option, "path_output"):
        return

    path_output: str = config.option.path_output

    cache: JupyterCacheBase = get_cache(Path(path_output) / "cache")  # type: ignore

    if len(cache.list_cache_records()) == 0:  # type: ignore
        return

    import subprocess
    from subprocess import CalledProcessError

    from .jupyter_book_run import JB_BINARY

    config_path = "_config.yml"
    args = [
        str(JB_BINARY),
        "build",
        f"--toc={toc_path}",
        f"--config={config_path}",
        f"--path-output={path_output}",
        str(config.rootdir),  # type: ignore
    ]
    try:
        terminalreporter.line(
            f"\n\n{_ts()} Nbmake building test report: {' '.join(args)}"
        )

        out = subprocess.check_output(args, stderr=subprocess.STDOUT)
        (Path(path_output) / "nbmake.log").write_bytes(out)

        url = (
            f"  file://{Path(path_output).absolute().as_posix()}/_build/html/index.html"
        )
        terminalreporter.line(
            f"\n\n{_ts()} Built test report (Open in browser).\n\n{url}\n"
        )
    except CalledProcessError as err:
        terminalreporter.line(
            f"\n\n{_ts()} (non-fatal) Nbmake failed to build test report:\n\n"
        )
        terminalreporter.line(err.output.decode())


def _ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
