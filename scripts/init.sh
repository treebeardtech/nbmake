#!/usr/bin/env bash

set -e
set +x

export PIP_USER=no

pipx install uv

uv venv --python 3.11.6
uv pip install -e .
uv run pre-commit run -a
uv run pre-commit install