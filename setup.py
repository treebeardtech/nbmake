import setuptools  # type: ignore

"""
nbmake
======

See [GitHub](https://github.com/treebeardtech/nbmake)
"""

install_requires = [
    "papermill",
    "click",
    "ipykernel",
    "pathlib",
    "nbstripout",
    "requests",
    "pydantic",
    "jupyter-contrib-nbextensions",  # for nbconvert scriptexporter
    "virtualenv",
]

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("src/nbmake/version.txt", "r") as fh:
    version = fh.read()

setuptools.setup(
    name="nbmake",
    version=version,
    author="Alex Remedios",
    author_email="alex@treebeard.io",
    description="automates notebook release processes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_namespace_packages(where="src"),
    package_dir={"": "src"},
    license="Apache-2.0",
    python_requires=">=3.6",
    package_data={"nbmake": ["version.txt"]},
    entry_points={"pytest11": ["nbmake = nbmake.pytest_plugin"],},
    install_requires=install_requires,
    url="https://github.com/treebeardtech/nbmake",
)
