# nbmake [Under Construction]
[![codecov](https://codecov.io/gh/treebeardtech/nbmake/branch/main/graph/badge.svg?token=9GuDM35FuO)](https://codecov.io/gh/treebeardtech/nbmake)
[![PyPI version](https://badge.fury.io/py/nbmake.svg)](https://badge.fury.io/py/nbmake)

Pytest plugin for testing notebooks

## Functionality

1. Runs notebooks individually through [jupyter-book](https://github.com/executablebooks/jupyter-book), supporting the same config options.
2. Works everywhere pytest does, allowing testing locally, on pre-commit, and in the cloud
3. Builds an HTML report of each test run which can be uploaded to hosting providers such as Netlify.

See [docs](https://treebeardtech.github.io/nbmake) to get started.

## Developing

### Install local package
```
poetry install
```

### Activate shell
```
poetry shell
```

### Run static checks
```
pre-commit run --all-files
pre-commit install
```

### Run tests
```
pytest
```

