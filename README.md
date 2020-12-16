# nbmake
[![codecov](https://codecov.io/gh/treebeardtech/nbmake/branch/main/graph/badge.svg?token=9GuDM35FuO)](https://codecov.io/gh/treebeardtech/nbmake)
[![PyPI versions](https://img.shields.io/pypi/pyversions/nbmake?logo=python&logoColor=white)](https://pypi.org/project/nbmake)
[![PyPI versions](https://img.shields.io/pypi/v/nbmake?logo=python&logoColor=white)](https://pypi.org/project/nbmake) [![Slack](https://img.shields.io/static/v1?label=slack&message=join&color=green&logo=slack)](https://join.slack.com/t/treebeard-entmoot/shared_invite/zt-jyvuqted-xBjnbvlfcu5P2ltBvn1~mg)

**What?** Pytest plugin for testing and releasing notebook documentation

**Why?** To raise the quality of scientific material through better automation

**Who is this for?** Research/Machine Learning Software Engineers who maintain packages/teaching materials with documentation written in notebooks.

## Functionality

1. Executes notebooks using pytest and nbclient, allowing parallel notebook testing
2. Optionally writes back to the repo, allowing faster building of [nbsphinx](https://github.com/spatialaudio/nbsphinx) or [jupyter book](https://github.com/executablebooks/jupyter-book) docs
3. Optionally builds an HTML report using [jupyter-book](https://github.com/executablebooks/jupyter-book) of the test run which can be uploaded to hosting providers such as Netlify.

**See [docs](https://treebeardtech.github.io/nbmake) to get started.**
<br/>
<br/>

## See Also

* [nbmake-action](https://github.com/treebeardtech/nbmake-action)

### HTML Report Example

![HTML Report](docs/screen.png)


## Developing

### Install local package
```
poetry install -E html
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

