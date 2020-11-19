# nbmake

Notebook testing Python plugin with a focus on observability

Features:

1. Test isolation: Runs each notebook as a test case inside its own virtualenv
2. Directives: Adds/removes cells at runtime to improve readability of output
3. Jupyter book integration: Test outputs can be built into a [Jupyter Book](https://jupyterbook.org/) for debugging

## Usage

```
pip install pytest nbmake
pytest --nbmake
```

the output is a Jupyter book in a build directory:

```
_build/
  html/ # contains jupyter book static site with test results
  jupyter_execute/ # contains built notebook ipynbs
```

## Directives

nbmake applies tags to notebooks based on directives in comments.

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

Directives will map to the following presentation options.
https://jupyterbook.org/interactive/hiding.html
