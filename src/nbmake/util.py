import pathlib
import sys

# https://stackoverflow.com/questions/19078969/python-getting-appdata-folder-in-a-cross-platform-way


def get_datadir():
    if sys.platform == "win32":
        return "AppData/Roaming"
    elif sys.platform == "linux":
        return ".local/share"
    elif sys.platform == "darwin":
        return "Library/Application Support"
    else:
        raise Exception(f"Don't know how to get data dir for platform {sys.platform}")


default_path_output = pathlib.Path.home() / get_datadir() / "nbmake"
try:
    default_path_output.mkdir(parents=True, exist_ok=True)
except:
    print(f"Failed to create data dir {default_path_output}, trying another")
    default_path_output = pathlib.Path(f"/tmp/nbmake")
    default_path_output.mkdir(parents=True, exist_ok=True)
