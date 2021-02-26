# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['nbmake']

package_data = \
{'': ['*']}

install_requires = \
['Pygments>=2.7.3,<3.0.0',
 'ipykernel>=5.4.0,<6.0.0',
 'nbclient>=0.3,<1.0',
 'nbformat>=5.0.8,<6.0.0',
 'pathlib>=1.0.1,<2.0.0',
 'pydantic>=1.7.2,<2.0.0',
 'pytest>=6.1.2,<7.0.0']

entry_points = \
{'pytest11': ['nbmake = nbmake.pytest_plugin']}

setup_kwargs = {
    'name': 'nbmake',
    'version': '0.3',
    'description': 'Pytest plugin for testing notebooks',
    'long_description': '# nbmake\n[![codecov](https://codecov.io/gh/treebeardtech/nbmake/branch/main/graph/badge.svg?token=9GuDM35FuO)](https://codecov.io/gh/treebeardtech/nbmake)\n[![PyPI versions](https://img.shields.io/pypi/pyversions/nbmake?logo=python&logoColor=white)](https://pypi.org/project/nbmake)\n[![PyPI versions](https://img.shields.io/pypi/v/nbmake?logo=python&logoColor=white)](https://pypi.org/project/nbmake) [![Slack](https://img.shields.io/static/v1?label=slack&message=join&color=green&logo=slack)](https://treebeard.io/slack) [![Twitter](https://img.shields.io/static/v1?label=twitter&message=follow&color=blue&logo=twitter)](https://twitter.com/treebeardtech)\n\n**What?** Pytest plugin for testing and releasing notebook documentation\n\n**Why?** To raise the quality of scientific material through better automation\n\n**Who is this for?** Research/Machine Learning Software Engineers who maintain packages/teaching materials with documentation written in notebooks.\n\n## Functionality\n\n1. Executes notebooks using pytest and nbclient, allowing parallel notebook testing\n2. Optionally writes back to the repo, allowing faster building of [nbsphinx](https://github.com/spatialaudio/nbsphinx) or [jupyter book](https://github.com/executablebooks/jupyter-book) docs\n3. Optionally builds an HTML report using [jupyter-book](https://github.com/executablebooks/jupyter-book) of the test run which can be uploaded to hosting providers such as Netlify.\n\n\n## Quick Start\n\n```\npip install pytest nbmake\npytest --nbmake **/*ipynb\n```\n\n## Allow errors and Configure Cell Timeouts\n\nnbmake is built on top of [nbclient](https://github.com/jupyter/nbclient) and designed to compatible with nbsphinx and jupyter-book.\n\nThe [jupyter book docs](https://jupyterbook.org/content/execute.html?highlight=allow_error#dealing-with-code-that-raises-errors) have a good description of how to ignore errors -- note that nbmake does not work with the external `_config.yml` configuration file. You must use the notebook JSON metadata field.\n\n## Parallelisation\n\nParallelisation with xdist is experimental upon initial release, but you can try it out:\n```\npip install pytest-xdist\n\npytest --nbmake -n=auto\n```\n\nIt is also possible to parallelise at a CI-level using strategies, see [example](https://github.com/LabForComputationalVision/plenoptic/blob/master/.github/workflows/treebeard.yml)\n\n### Build Jupyter Books Faster\n\nUsing xdist and the `--overwrite` flag let you build a large jupyter book repo faster:\n\n```\npytest --nbmake --overwrite -n=auto examples\njb build examples\n```\n## Advice on Usage\n\nnbmake is best used in a scenario where you use the ipynb files only for development. Consumption of notebooks is primarily done via a docs site, built through jupyter book, nbsphinx, or some other means. If using one of these tools, you are able to write assertion code in cells which will be [hidden from readers](https://jupyterbook.org/interactive/hiding.html).\n\n### Pre-commit\n\nTreating notebooks like source files lets you keep your repo minimal. Some tools, such as plotly may drop several megabytes of javascript in your output cells, as a result, stripping out notebooks on pre-commit is advisable:\n\n```\n# .pre-commit-config.yaml\nrepos:\n  - repo: https://github.com/kynan/nbstripout\n    rev: master\n    hooks:\n      - id: nbstripout\n```\n\nSee https://pre-commit.com/ for more...\n\n## Disable Nbmake\n\nImplicitly:\n```\npytest\n```\n\nExplicitly:\n```\npytest -p no:nbmake\n```\n\n## See Also:\n\n* [nbmake action](https://github.com/treebeardtech/treebeard)\n* [pytest](https://pytest.org/)\n* [jupyter book](https://github.com/executablebooks/jupyter-book)\n* [jupyter cache](https://github.com/executablebooks/jupyter-cache)\n* [MyST-NB](https://github.com/executablebooks/MyST-NB)\n',
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
