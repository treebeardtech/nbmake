import subprocess
import sys
from datetime import datetime
from pathlib import Path
from subprocess import CalledProcessError
from typing import List, Optional

import yaml

JB = Path(sys.executable).parent / "jb"


def create_report(terminalreporter, path_output: Path, verbose: int):
    (path_output / "_build" / "report_config.yml").write_text(
        yaml.dump(
            {
                "execute": {
                    "execute_notebooks": "off",
                    # "only_build_toc_files": True,
                },
            }
        )
    )
    toc_path = Path(path_output) / "_build" / "_toc.yml"

    from .jupyter_book_adapter import build

    config_path = path_output / "_build" / "report_config.yml"

    index_path = Path(path_output) / "_build" / "html" / "index.html"
    url = f"file://{index_path.absolute().as_posix()}"
    terminalreporter.line(f"\n\n{ts()} nbmake building test report at: \n\n  {url}\n")
    msg = ""

    if not JB.exists():
        print(
            f"Non-fatal error: Cannot build test report as jupyter-book executable not found at {JB}.\n\nDo you need to `pip install 'nbmake[html]'`?\n"
        )
        return

    msg = build(
        path_output / "_build" / "nbmake",
        path_output,
        config_path,
        toc_path,
        verbose=bool(verbose),
    )

    if index_path.exists() and msg is None:
        terminalreporter.line(f"{ts()} done.")
    else:
        terminalreporter.line(
            f"{ts()} Non-fatal error building final test report: \n\n{msg}"
        )


def build(
    source: Path,
    out: Optional[Path] = None,
    config: Optional[Path] = None,
    toc: Optional[Path] = None,
    verbose: Optional[bool] = False,
) -> Optional[str]:
    args: List[str] = [str(JB), "build", str(source)]

    if out:
        args += ["--path-output", str(out)]

    if config:
        args += [
            "--config",
            str(config),
        ]

    if toc:
        args += ["--toc", str(toc), "-q", "-n"]

    if verbose:
        args.append("-v")
    try:
        if verbose:
            print(f"\nnbmake: Running {' '.join(args)}")
        output = subprocess.check_output(args, stderr=subprocess.STDOUT)
        if verbose:
            print(output.decode())
    except CalledProcessError as err:
        return f"\nnbmake: the jupyter-book command failed.\n\n{err.output.decode()}"


def ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
