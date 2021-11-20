
#!/usr/bin/env bash

set -e
set +x

printenv

which python

export PIP_USER=no

pip install poetry

poetry install
poetry run pre-commit run -a
poetry run pre-commit install