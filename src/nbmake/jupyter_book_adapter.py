import os
import subprocess
from pathlib import Path
from subprocess import CalledProcessError
from typing import List, Optional

import jupyter_book

jb_path: str = jupyter_book.__file__
JB_BINARY: Path = (
    Path(os.path.dirname(jb_path))
    / ("../../../Scripts/jb.exe" if os.name == "nt" else "../../../../bin/jb")
).resolve()


def build(
    source: Path,
    out: Optional[Path] = None,
    config: Optional[Path] = None,
    toc: Optional[Path] = None,
):
    args: List[str] = [str(JB_BINARY), "build", str(source)]

    if out:
        args += ["--path-output", str(out)]

    if config:
        args += [
            "--config",
            str(config),
        ]

    if toc:
        args += ["--toc", str(toc)]

    try:
        print(f"\nnbmake: Running {' '.join(args)}")
        subprocess.check_output(args, stderr=subprocess.STDOUT)
    except CalledProcessError as err:
        print(f"\nnbmake: the jupyter-book command failed.\n\n{err.output.decode()}")
