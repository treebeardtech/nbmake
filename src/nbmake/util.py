import pathlib
import sys

# https://stackoverflow.com/questions/19078969/python-getting-appdata-folder-in-a-cross-platform-way


def get_datadir() -> pathlib.Path:
    if sys.platform == "win32":
        return "AppData/Roaming"
    elif sys.platform == "linux":
        return ".local/share"
    elif sys.platform == "darwin":
        return "Library/Application Support"
    else:
        raise Exception(f"Don't know how to get data dir for platform {sys.platform}")


data_dir = pathlib.Path.home() / get_datadir() / "nbmake"
try:
    data_dir.mkdir(parents=True, exist_ok=True)
except:
    try:
        print(f"Failed to create data dir {data_dir}, trying another")
        data_dir = pathlib.Path(f"/tmp/nbmake")
        data_dir.mkdir(parents=True, exist_ok=True)
    except:
        print(f"Failed to create data dir {data_dir}, trying another")
        data_dir = pathlib.Path(f".nbmake").absolute()
        data_dir.mkdir(parents=True, exist_ok=True)
