from datetime import datetime
from pathlib import Path
from traceback import print_exc
from typing import Any, Optional

import yaml
from _pytest.config import Config

from .pytest_items import NotebookFile


def pytest_addoption(parser: Any):
    group = parser.getgroup("nbmake", "notebook testing")
    group.addoption(
        "--nbmake", action="store_true", help="Test notebooks", default=False
    )
    group.addoption(
        "--overwrite", action="store_true", help="Create HTML report", default=False
    )
    group.addoption(
        "--path-output",
        action="store",
        help="Location for _build/html and _build/.jupyter_cache dirs, default is root directory.",
    )


def pytest_collect_file(path: str, parent: Any) -> Optional[Any]:
    opt = parent.config.option
    p = Path(path)
    if opt.nbmake and p.match("*ipynb") and "_build" not in p.parts:
        return NotebookFile.from_parent(parent, fspath=path)

    return None


def pytest_configure(config: Config):
    option = config.option
    if not option.nbmake:
        return

    if not option.path_output:
        return

    # import shutil
    # staging_dir=str(Path('_build') /'nbmake')
    # shutil.rmtree(staging_dir)
    # shutil.copytree('.', staging_dir, ignore=shutil.ignore_patterns('_build'))


def pytest_collection_finish(session: Any) -> None:
    option = session.config.option
    if not option.nbmake:
        return
    path_output: str = session.config.option.path_output

    if not path_output:
        return

    toc_path = Path(path_output) / "_build" / "_toc.yml"
    toc_path.parent.mkdir(parents=True, exist_ok=True)
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
    if not option.nbmake or not option.path_output:
        return

    try:
        path_output = Path(option.path_output)
        (path_output / "_build" / "report_config.yml").write_text(
            yaml.dump(
                {
                    "execute": {
                        "execute_notebooks": "off",
                        "only_build_toc_files": True,
                    },
                }
            )
        )
        toc_path = Path(path_output) / "_build" / "_toc.yml"

        from .jupyter_book_adapter import build

        config_path = path_output / "_build" / "report_config.yml"

        index_path = Path(path_output) / "_build" / "html" / "index.html"
        url = f"file://{index_path.absolute().as_posix()}"
        terminalreporter.line(
            f"\n\n{_ts()} nbmake building test report at: \n\n  {url}\n"
        )
        msg = build(
            path_output / "_build" / "nbmake",
            path_output,
            config_path,
            toc_path,
            verbose=bool(option.verbose),
        )

        if index_path.exists() and msg is None:
            terminalreporter.line(f"{_ts()} done.")
        else:
            terminalreporter.line(
                f"{_ts()} Non-fatal error building final test report: {msg}"
            )
    except:
        terminalreporter.line(
            f"{_ts()} Non-fatal error building final test report: {print_exc()}"
        )


def _ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
