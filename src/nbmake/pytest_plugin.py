from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import yaml
from _pytest.config import Config
from jupyter_cache import get_cache
from jupyter_cache.cache.main import JupyterCacheBase

from .pytest_items import NotebookFile
from .util import default_path_output


def pytest_addoption(parser: Any):
    group = parser.getgroup("nbmake", "notebook testing")
    group.addoption(
        "--nbmake", action="store_true", help="Test notebooks", default=False
    )
    group.addoption(
        "--html", action="store_true", help="Create HTML report", default=False
    )
    group.addoption(
        "--path-output",
        action="store",
        help="Location for _build/html and _build/.jupyter_cache dirs, default is root directory.",
    )


def pytest_configure(config: Config):
    option = config.option
    if not option.nbmake:
        return

    if not option.path_output:
        if option.html:
            config.option.path_output = config.rootdir
        else:
            config.option.path_output = default_path_output

    path_out: Path = Path(config.option.path_output)
    (path_out / "_build").mkdir(exist_ok=True, parents=True)

    (path_out / "_build" / "report_config.yml").write_text(
        yaml.dump(
            {
                "exclude_patterns": ["_build", ".*/*", ".*/**/*"],
                "only_build_toc_files": True,
                "execute": {
                    "execute_notebooks": "cache",
                    "cache": str(path_out / "_build" / ".jupyter_cache"),
                },
            }
        )
    )


def pytest_collect_file(path: str, parent: Any) -> Optional[Any]:
    opt = parent.config.option
    p = Path(path)
    if opt.nbmake and p.match("*ipynb") and "_build" not in p.parts:
        return NotebookFile.from_parent(parent, fspath=path)

    return None


def pytest_collection_finish(session: Any) -> None:
    option = session.config.option
    if not option.nbmake:
        return
    path_output: str = session.config.option.path_output
    toc_path = Path(path_output) / "_build" / "_toc.yml"
    nb_items = [
        Path(i.filename) for i in session.items if hasattr(session.items[0], "nbmake")
    ]
    if len(nb_items) == 0:
        return

    toc = [{"file": str(f).replace(".ipynb", "")} for f in nb_items]
    toc[0]["title"] = "test results"
    toc_path.write_text(yaml.dump(toc))
    if session.config.option.verbose > 0:
        print(f"nbmake: Wrote toc to {toc_path}")


def pytest_terminal_summary(terminalreporter: Any, exitstatus: int, config: Config):
    option = config.option
    if not (option.nbmake and option.html):
        return
    try:
        option: Any = config.option
        if not hasattr(option, "path_output"):
            return

        path_output = Path(config.option.path_output)
        toc_path = Path(path_output) / "_build" / "_toc.yml"

        cache: JupyterCacheBase = get_cache(path_output / "_build" / ".jupyter_cache")

        if len(cache.list_cache_records()) == 0:
            return

        from .jupyter_book_adapter import build

        config_path = path_output / "_build" / "report_config.yml"

        index_path = Path(path_output) / "_build" / "html" / "index.html"
        url = f"file://{index_path.as_posix()}"
        terminalreporter.line(
            f"\n\n{_ts()} nbmake building test report at: \n\n  {url}\n"
        )
        build(
            Path(config.rootdir),
            path_output,
            config_path,
            toc_path,
            verbose=bool(option.verbose),
        )
        if index_path.exists():
            terminalreporter.line(f"{_ts()} done.")
        else:
            terminalreporter.line(f"{_ts()} Non-fatal error building final test report")
    except:
        terminalreporter.line(f"{_ts()} Non-fatal error building final test report")


def _ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
