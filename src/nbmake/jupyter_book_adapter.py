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
