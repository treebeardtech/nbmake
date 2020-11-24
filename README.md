# nbmake

Pytest plugin for testing notebooks

## Functionality

1. Runs notebooks as pytest testcases, from top to bottom
2. Builds outputs into a Jupyter book
3. Allows altering of notebok runtime behaviour and cosmetics

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
  nbmake_execute/ # contains nbmake ipynbs
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

## Directives

Directives automate release tasks and are removed after being processed unless:

- `--dev` is passed
- The notebook fails

### Test Directives

```
# nbmake: xfail
```

Will allow the cell to fail.

### Cosmetic Directives

nbmake applies tags to notebooks based on directives in comments.

Directives will map to the following presentation options.
https://jupyterbook.org/interactive/hiding.html

To make prod output appear different to what is run (e.g. for assertions/diagnostics):

e.g.

```
# nbmake: hide-cell
assert x = 42
```

Will result in the built notebook containing:

```
metadata: {
    tags: [ hide-cell ]
}
```
