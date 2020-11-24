# nbmake [Under Construction]

Pytest plugin for building notebooks into a tested Jupyterbook

## Functionality

1. Implements the pytest plugin API allowing parallel execution of notebooks via `pytest-xdist`
2. Treats the `_toc.yml` as the test file, and each notebook as a test case.
3. Runs each file through jupyterbook's execution layer separately, then re-combines and builds the book

## Usage

### During Development

```
pip install pytest nbmake
pytest --nbmake
```

the output is a Jupyter book in a build directory:

```
_build/
  html/ # contains jupyter book static site with test results
  jupyter_execute/ # contains jupyter-book ipynbs
```

this can be viewed locally for debugging

```
open _build/html/index.html
```

## Example release process

```
pytest --nbmake
netlify deploy dir=_build/html
```

## Roadmap

Just some ideas:

### Test Isolation

Improve virtualisation of individual tests, e.g. to prevent `!pip install` commands contaminating the test environment.

### Pytest Fixture Integration

Make notebooks a first-class pytest citizen by providing a mechanism for enabling pytest fixtures
