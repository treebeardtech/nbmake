# nbmake
[![codecov](https://codecov.io/gh/treebeardtech/nbmake/branch/main/graph/badge.svg?token=9GuDM35FuO)](https://codecov.io/gh/treebeardtech/nbmake)
[![PyPI versions](https://img.shields.io/pypi/pyversions/nbmake?logo=python&logoColor=white)](https://pypi.org/project/nbmake)
[![PyPI versions](https://img.shields.io/pypi/v/nbmake?logo=python&logoColor=white)](https://pypi.org/project/nbmake) [![Slack](https://img.shields.io/static/v1?label=slack&message=join&color=green&logo=slack)](https://treebeard.io/slack) [![Twitter](https://img.shields.io/static/v1?label=twitter&message=follow&color=blue&logo=twitter)](https://twitter.com/treebeardtech)

**What?** Pytest plugin for testing and releasing notebook documentation

**Why?** To raise the quality of scientific material through better automation

**Who is this for?** Research/Machine Learning Software Engineers who maintain packages/teaching materials with documentation written in notebooks.

## Functionality

1. Executes notebooks using pytest and nbclient, allowing parallel notebook testing
2. Optionally writes back to the repo, allowing faster building of [nbsphinx](https://github.com/spatialaudio/nbsphinx) or [jupyter book](https://github.com/executablebooks/jupyter-book) docs
3. Optionally builds an HTML report using [jupyter-book](https://github.com/executablebooks/jupyter-book) of the test run which can be uploaded to hosting providers such as Netlify.


## Quick Start

```
pip install pytest nbmake
pytest --nbmake **/*ipynb
```

## Allow errors and Configure Cell Timeouts

nbmake is built on top of [nbclient](https://github.com/jupyter/nbclient) and designed to compatible with nbsphinx and jupyter-book.

The [jupyter book docs](https://jupyterbook.org/content/execute.html?highlight=allow_error#dealing-with-code-that-raises-errors) have a good description of how to ignore errors -- note that nbmake does not work with the external `_config.yml` configuration file. You must use the notebook JSON metadata field.

## Parallelisation

Parallelisation with xdist is experimental upon initial release, but you can try it out:
```
pip install pytest-xdist

pytest --nbmake -n=auto
```

It is also possible to parallelise at a CI-level using strategies, see [example](https://github.com/LabForComputationalVision/plenoptic/blob/master/.github/workflows/treebeard.yml)

### Build Jupyter Books Faster

Using xdist and the `--overwrite` flag let you build a large jupyter book repo faster:

```
pytest --nbmake --overwrite -n=auto examples
jb build examples
```
## Advice on Usage

nbmake is best used in a scenario where you use the ipynb files only for development. Consumption of notebooks is primarily done via a docs site, built through jupyter book, nbsphinx, or some other means. If using one of these tools, you are able to write assertion code in cells which will be [hidden from readers](https://jupyterbook.org/interactive/hiding.html).

### Pre-commit

Treating notebooks like source files lets you keep your repo minimal. Some tools, such as plotly may drop several megabytes of javascript in your output cells, as a result, stripping out notebooks on pre-commit is advisable:

```
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/kynan/nbstripout
    rev: master
    hooks:
      - id: nbstripout
```

See https://pre-commit.com/ for more...

## Disable Nbmake

Implicitly:
```
pytest
```

Explicitly:
```
pytest -p no:nbmake
```

## See Also:

* [nbmake action](https://github.com/treebeardtech/treebeard)
* [pytest](https://pytest.org/)
* [jupyter book](https://github.com/executablebooks/jupyter-book)
* [jupyter cache](https://github.com/executablebooks/jupyter-cache)
* [MyST-NB](https://github.com/executablebooks/MyST-NB)
