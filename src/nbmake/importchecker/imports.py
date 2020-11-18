import glob
import importlib
import os
import re
import sys
from typing import Any, Set

import click
from nbconvert import ScriptExporter  # type: ignore

from_regexp = re.compile(r"^from (\w+)")
import_regexp = re.compile(r"^import (\w+)")


def get_imported_modules(glob_path: str) -> Set[str]:
    nb_paths = glob.glob(glob_path, recursive=True)
    if len(nb_paths) == 0:
        raise Exception(f"No notebooks found with glob {glob_path}, cwd {os.getcwd()}")

    se: Any = ScriptExporter()

    all_imported_modules = set()
    for path in nb_paths:
        try:
            [script, _] = se.from_filename(path)
        except Exception as ex:
            click.echo(f"Import checker cannot read {path}\n{ex}")
            continue
        lines = script.split("\n")

        for line in lines:
            from_match = from_regexp.match(line)
            if from_match:
                all_imported_modules.add(from_match.group(1))
                continue

            import_match = import_regexp.match(line)
            if import_match:
                all_imported_modules.add(import_match.group(1))
                continue

    return all_imported_modules


def get_installed_modules(imported_modules: Set[str]) -> Set[str]:
    modules = set()
    # Disable stdout/stderr to prevent log spam while importing
    save_stdout = sys.stdout
    save_stderr = sys.stderr
    sys.stderr = open("trash", "w")
    sys.stdout = open("trash", "w")

    for im in imported_modules:
        try:
            importlib.import_module(im)
            modules.add(im)
            # print(f"imported {im}", file=save_stdout)
        except:
            pass
            # print(f"failed to import {im}", file=save_stdout)
    sys.stdout = save_stdout
    sys.stderr = save_stderr
    return modules


def is_local_module(module_name: str):
    # is there a <name>.py or <name> directory
    dirs = glob.glob(f"**/{module_name}", recursive=True)
    scripts = glob.glob(f"**/{module_name}.py", recursive=True)

    return dirs or scripts


def check_imports(glob_path: str = "**/*ipynb"):
    out = ""
    out += f"🌲 Checking for potentially missing imports...\n\n"
    imported_modules = get_imported_modules(glob_path)
    installed_modules = get_installed_modules(imported_modules)

    missing_modules = list(
        filter(
            lambda m: not is_local_module(m),
            imported_modules.difference(installed_modules),
        )
    )

    if len(missing_modules) > 0:
        out += f"\n❗📦 You *may* be missing project requirements, the following modules are imported from your notebooks but can't be imported from your project root directory\n\n"

        for module in sorted(missing_modules):
            out += f"  - {module}\n"
        return False, out
    else:
        out += "\n✨ All notebook imports appear to be backed by a reproducible dependency file!\n"
        return True, out


if __name__ == "__main__":
    glob_path = sys.argv[1] if len(sys.argv) > 1 else "**/*ipynb"
    click.echo(check_imports(glob_path))
