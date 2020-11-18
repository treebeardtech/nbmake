import os


def clean_log_file():
    if os.path.exists("nbmake.log"):
        os.remove("nbmake.log")
