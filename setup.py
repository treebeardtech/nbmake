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
 'Pygments>=2.7.3,<3.0.0',
 'ipykernel>=5.4.0,<6.0.0',
 'nbclient<0.4',
 'nbformat>=5.0.8,<6.0.0',
 'pathlib>=1.0.1,<2.0.0',
 'pydantic>=1.7.2,<2.0.0',
 'pytest>=6.1.2,<7.0.0']

extras_require = \
{'html': ['jupyter-book>=0.8.3,<0.9.0']}

entry_points = \
{'pytest11': ['nbmake = nbmake.pytest_plugin']}

setup_kwargs = {
    'name': 'nbmake',
    'version': '0.1',
    'description': 'Pytest plugin for testing notebooks',
    'long_description': '# nbmake [Under Construction]\n[![codecov](https://codecov.io/gh/treebeardtech/nbmake/branch/main/graph/badge.svg?token=9GuDM35FuO)](https://codecov.io/gh/treebeardtech/nbmake)\n[![PyPI version](https://badge.fury.io/py/nbmake.svg)](https://badge.fury.io/py/nbmake)\n\nPytest plugin for testing notebooks\n\n## Functionality\n\n1. Executes notebooks using pytest and nbclient, allowing parallel notebook testing\n2. Lets you automate release processes from your laptop or in the cloud\n3. Optionally builds an HTML report using [jupyter-book](https://github.com/executablebooks/jupyter-book) of the test run which can be uploaded to hosting providers such as Netlify.\n\nSee [docs](https://treebeardtech.github.io/nbmake) to get started.\n\n### HTML Report Example\n\n![HTML Report](docs/screen.png)\n\n\n## Developing\n\n### Install local package\n```\npoetry install -E html\n```\n\n### Activate shell\n```\npoetry shell\n```\n\n### Run static checks\n```\npre-commit run --all-files\npre-commit install\n```\n\n### Run tests\n```\npytest\n```\n\n',
    'author': 'alex-treebeard',
    'author_email': 'alex@treebeard.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/treebeardtech/nbmake',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
