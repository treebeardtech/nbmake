from pathlib import Path
from typing import Any, Optional

import yaml
from _pytest.config import Config

from .jupyter_book_adapter import create_report
from .pytest_items import NotebookFile


def pytest_addoption(parser: Any):
    group = parser.getgroup("nbmake", "notebook testing")
    group.addoption(
        "--nbmake", action="store_true", help="Test notebooks", default=False
    )
    group.addoption(
        "--overwrite",
        action="store_true",
        help="Overwrite the source ipynbs",
        default=False,
    )
    group.addoption(
        "--path-output",
        action="store",
        help="Create a test report in {path-output}/_build/html. Requires pip install 'nbmake[html]'",
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

    create_report(terminalreporter, Path(option.path_output), option.verbose)
