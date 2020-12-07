import uuid
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, Optional

import yaml
from _pytest.config import Config
from jupyter_cache import get_cache
from jupyter_cache.cache.main import JupyterCacheBase

from .pytest_items import NotebookFile, NotebookItem
from .util import data_dir


class NbMakePaths:
    config: Optional[Path]
    toc: Optional[Path]
    output: Optional[Path]


def pytest_addoption(parser: Any):
    group = parser.getgroup("nbmake", "notebook testing")
    group.addoption("--nbmake", action="store_true", help="Test notebooks")

    default_path_output = data_dir / str(uuid.uuid4())
    default_path_output.mkdir(exist_ok=True, parents=True)

    group.addoption("--jbconfig", action="store", help="Your jupyter-book config file")
    group.addoption("--path-output", action="store", default=str(default_path_output))


def pytest_configure(config: Config):
    path_out: Path = Path(config.option.path_output)

    (path_out / "report_config.yml").write_text(
        yaml.dump(
            {
                "exclude_patterns": [".*/**/*", "Library/**/*", ".pytest_cache/**/*"],
                "execute": {
                    "execute_notebooks": "cache",
                    "cache": str(path_out / "cache"),
                    # "only_build_toc_files": True
                },
            }
        )
    )


def pytest_collect_file(path: str, parent: Any) -> Optional[Any]:
    opt = parent.config.option
    if opt.nbmake and fnmatch(path, "*.ipynb"):
        return NotebookFile.from_parent(parent, fspath=path)

    return None


def pytest_collection_finish(session: Any) -> None:
    path_output: str = session.config.option.path_output
    toc_path = Path(path_output) / "_toc.yml"
    nb_items = [Path(i.filename) for i in session.items if isinstance(i, NotebookItem)]
    if len(nb_items) == 0:
        return

    toc = [{"file": str(f).replace(".ipynb", "")} for f in nb_items]
    toc[0]["title"] = "test results"
    toc_path.write_text(yaml.dump(toc))


def pytest_terminal_summary(terminalreporter: Any, exitstatus: int, config: Config):
    option: Any = config.option
    if not hasattr(option, "path_output"):
        return

    path_output = Path(config.option.path_output)
    toc_path = Path(path_output) / "_toc.yml"

    cache: JupyterCacheBase = get_cache(path_output / "cache")

    if len(cache.list_cache_records()) == 0:
        return

    import subprocess
    from subprocess import CalledProcessError

    from .jupyter_book_run import JB_BINARY

    config_path = path_output / "report_config.yml"
    args = [
        str(JB_BINARY),
        "build",
        f"--toc={str(toc_path)}",
        f"--config={config_path}",
        f"--path-output={path_output}",
        str(config.rootdir),
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
