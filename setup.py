# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['nbmake']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.3.1,<6.0.0',
 'jupyter-book[html]>=0.8.3,<0.9.0',
 'nbclient<0.4',
 'nbformat>=5.0.8,<6.0.0',
 'pathlib>=1.0.1,<2.0.0',
 'pydantic>=1.7.2,<2.0.0',
 'pytest>=6.1.2,<7.0.0']

entry_points = \
{'pytest11': ['nbmake = nbmake.pytest_plugin']}

setup_kwargs = {
    'name': 'nbmake',
    'version': '0.0.1',
    'description': 'Pytest plugin for releasing notebooks',
    'long_description': '# nbmake [Under Construction]\n[![codecov](https://codecov.io/gh/treebeardtech/nbmake/branch/main/graph/badge.svg?token=9GuDM35FuO)](https://codecov.io/gh/treebeardtech/nbmake)\n[![PyPI version](https://badge.fury.io/py/nbmake.svg)](https://badge.fury.io/py/nbmake)\n\nPytest plugin for testing notebooks\n\n## Functionality\n\n1. Runs notebooks individually through [jupyter-book](https://github.com/executablebooks/jupyter-book), allowing the same options such as allowing exceptions on individual cells.\n2. Works everywhere pytest does, allowing testing locally, on pre-commit, and in the cloud\n3. Optionally builds an HTML report of the test run which can be uploaded to hosting providers such as Netlify.\n\nSee [docs](https://treebeardtech.github.io/nbmake) to get started.\n\n### HTML Report Example\n\n![HTML Report](docs/screen.png)\n\n\n\n## Developing\n\n### Install local package\n```\npoetry install\n```\n\n### Activate shell\n```\npoetry shell\n```\n\n### Run static checks\n```\npre-commit run --all-files\npre-commit install\n```\n\n### Run tests\n```\npytest\n```\n\n',
    'author': 'alex-treebeard',
    'author_email': 'alex@treebeard.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/treebeardtech/nbmake',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
