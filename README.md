# nbmake

Pytest plugin for building notebooks into a tested Jupyterbook

## Functionality

1. Implements pytest plugin API to access the Jupyterbook execution runtime
   1. This enables parallelisation with `pytest-xdist`
2. Automates generation of Jupyterbook config and table of contents, or lets you provide your own
3. Does not interfere with normal jupyter-book usage.

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
