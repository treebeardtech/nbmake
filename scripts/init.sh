#!/usr/bin/env bash

set -e
set +x

export PIP_USER=no

pip install poetry

poetry install
poetry run pre-commit run -a
poetry run pre-commit install