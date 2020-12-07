# -*- coding: utf-8 -*-

# DO NOT EDIT THIS FILE!
# This file has been autogenerated by dephell <3
# https://github.com/dephell/dephell

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


import os.path

readme = ""
here = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(here, "README.rst")
if os.path.exists(readme_path):
    with open(readme_path, "rb") as stream:
        readme = stream.read().decode("utf8")


setup(
    long_description=readme,
    name="nbmake",
    version="0.0.1",
    description="Pytest plugin for releasing notebooks",
    python_requires="==3.*,>=3.6.1",
    project_urls={"homepage": "https://github.com/treebeardtech/nbmake"},
    author="alex-treebeard",
    author_email="alex@treebeard.io",
    license="Apache-2.0",
    entry_points={"pytest11": ["nbmake = nbmake.pytest_plugin"]},
    packages=[],
    package_dir={"": "src"},
    package_data={},
    install_requires=[
        "jupyter-book",
        "jupyter-cache[cli]==0.*,>=0.4.1",
        "pathlib==1.*,>=1.0.1",
        "pydantic==1.*,>=1.7.2",
        "pytest==6.*,>=6.1.2",
        "pyyaml==5.*,>=5.3.1",
    ],
    dependency_links=[
        "git+https://github.com/alex-treebeard/jupyter-book.git#egg=jupyter-book"
    ],
    extras_require={
        "dev": [
            "dephell==0.*,>=0.8.3",
            "pre-commit==2.*,>=2.8.2",
            "pytest-cov==2.*,>=2.10.1",
            "pytest-xdist==2.*,>=2.1.0",
            "virtualenv==20.*,>=20.1.0",
        ]
    },
)
