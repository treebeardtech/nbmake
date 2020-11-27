# nbmake [Under Construction]
[![codecov](https://codecov.io/gh/treebeardtech/nbmake/branch/main/graph/badge.svg?token=9GuDM35FuO)](https://codecov.io/gh/treebeardtech/nbmake)

Pytest plugin for testing Python 3 notebooks

## Functionality

1. Implements the pytest plugin API allowing parallel execution of notebooks via `pytest-xdist`
2. Runs notebooks using `jupyter-book`, using the `_config.yml` and writing to the `jupyter-cache`

This enables fast testing and creation of doc sites.

## Usage

### Quickstart

```bash
pip install pytest nbmake
pytest --nbmake
```

### Parallelise

```bash
pip install pytest-xdist
pytest --nbmake -n=auto
```

### Pre-cache your Jupyter Book

```bash
pytest --nbmake --jbconfig=_config.yml
jb build .
```

## Developer Setup

Install local package
```
poetry install
```

Activate shell
```
poetry shell
```

Run static checks
```
pre-commit run --all-files
pre-commit install
```

Run tests
```
pytest
```