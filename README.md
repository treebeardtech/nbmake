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

outputs

```
_nbmake/
  output/
    nb.ipynb
  report/
    ...
    index.html
```

## Directives

To hide a cell containing assertions after executing:

```
# nbmake: hide
```

To replace a cell with cells from a boilerplate notebook

```
# nbmake: insert boilerplate.ipynb
```
