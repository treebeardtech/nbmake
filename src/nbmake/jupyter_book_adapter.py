import subprocess
import sys
from pathlib import Path
from subprocess import CalledProcessError
from typing import List, Optional

JB = Path(sys.executable).parent / "jb"


def build(
    source: Path,
    out: Optional[Path] = None,
    config: Optional[Path] = None,
    toc: Optional[Path] = None,
):
    args: List[str] = [str(JB), "build", str(source)]

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
        output = subprocess.check_output(args, stderr=subprocess.STDOUT)
        print(output.decode())
    except CalledProcessError as err:
        print(f"\nnbmake: the jupyter-book command failed.\n\n{err.output.decode()}")
