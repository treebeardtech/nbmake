# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = {"": "src"}

packages = ["nbmake"]

package_data = {
    "": ["*"],
    "nbmake": [
        "typestubs/_pytest/*",
        "typestubs/_pytest/pytester/*",
        "typestubs/jupyter_book/*",
        "typestubs/nbformat/*",
        "typestubs/nbformat/v4/*",
        "typestubs/pydantic/*",
        "typestubs/pytest/*",
    ],
}

install_requires = [
    "PyYAML>=5.3.1,<6.0.0",
    "jupyter-book>=0.8.3,<0.9.0",
    "jupyter-cache[cli]>=0.4.1,<0.5.0",
    "pathlib>=1.0.1,<2.0.0",
    "pydantic>=1.7.2,<2.0.0",
    "pytest>=6.1.2,<7.0.0",
]

entry_points = {"pytest11": ["nbmake = nbmake.plugin"]}

setup_kwargs = {
    "name": "nbmake",
    "version": "0.0.1",
    "description": "Pytest plugin for releasing notebooks",
    "long_description": "# nbmake [Under Construction]\n[![codecov](https://codecov.io/gh/treebeardtech/nbmake/branch/main/graph/badge.svg?token=9GuDM35FuO)](https://codecov.io/gh/treebeardtech/nbmake)\n\nPytest plugin for testing Python 3 notebooks\n\n## Functionality\n\n1. Implements the pytest plugin API allowing parallel execution of notebooks via `pytest-xdist`\n2. Runs notebooks using `jupyter-book`, using the `_config.yml` and writing to the `jupyter-cache`\n\nThis enables fast testing and creation of doc sites.\n\n## Usage\n\n### Quickstart\n\n```bash\npip install pytest nbmake\npytest --nbmake\n```\n\n### Parallelise\n\n```bash\npip install pytest-xdist\npytest --nbmake -n=auto\n```\n\n### Pre-cache your Jupyter Book\n\n```bash\npytest --nbmake --jbconfig=_config.yml\njb build .\n```\n\n## Developer Setup\n\nInstall local package\n```\npoetry install\n```\n\nActivate shell\n```\npoetry shell\n```\n\nRun static checks\n```\npre-commit run --all-files\npre-commit install\n```\n\nRun tests\n```\npytest\n```",
    "author": "alex-treebeard",
    "author_email": "alex@treebeard.io",
    "maintainer": None,
    "maintainer_email": None,
    "url": "https://github.com/treebeardtech/nbmake",
    "package_dir": package_dir,
    "packages": packages,
    "package_data": package_data,
    "install_requires": install_requires,
    "entry_points": entry_points,
    "python_requires": ">=3.6.1,<4.0.0",
}


setup(**setup_kwargs)
