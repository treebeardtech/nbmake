# nbmake [Under Construction]
[![codecov](https://codecov.io/gh/treebeardtech/nbmake/branch/main/graph/badge.svg?token=9GuDM35FuO)](https://codecov.io/gh/treebeardtech/nbmake)
[![PyPI version](https://badge.fury.io/py/nbmake.svg)](https://badge.fury.io/py/nbmake)

Pytest plugin for testing Python 3 notebooks

## Functionality

1. Implements the pytest plugin API allowing parallel execution of notebooks via `pytest-xdist`
2. Uses `jupyter-book` as a runtime, enabling caching for jupyter book builds and supporting the same presentation/execution options.

This facilitates building compute-intensive documentation. See [docs](https://treebeardtech.github.io/nbmake) to get started.

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

