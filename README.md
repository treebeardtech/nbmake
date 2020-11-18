# nbmake

## Development Install

This directory (`nbmake-lib`) contains the python package which runs notebooks and finds missing imports.

Before getting into python, ensure you have installed `node` and `pyright` installed which lets us use Python type-checking.

## Validate GitHub action NPM config

Run the following from **repo root** to ensure the github action typescript code is pointed at your current branch's Python code.

`npm run all`

## Install Python Packages in `nbmake-lib`

Run from **nbmake-lib**

```
pipenv install --dev
```

## Development against Backend

You probable won't need this section as most of the code doesn't use the back end...

To run against local services

## Code Quality Checks

Clone typeshed into the **repo root** so that Pyright knows about common Python pkgs.

```bash
git clone https://github.com/python/typeshed.git
```

Check types and then formatting

```
pyright && black --check .
```

Organise imports!

```
isort -m 3 -tc -y
```
