# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.148.1/containers/python-3/.devcontainer/base.Dockerfile

# [Choice] Python version: 3, 3.9, 3.8, 3.7, 3.6
ARG VARIANT="3.11"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

# [Option] Install Node.js
ARG INSTALL_NODE="true"
ARG NODE_VERSION="lts/*"
RUN if [ "${INSTALL_NODE}" = "true" ]; then su vscode -c "source /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} 2>&1"; fi

USER vscode
RUN pip3 --disable-pip-version-check --no-cache-dir install -U \
  'poetry==1.1.13' \
  'pip==22.1.2'

COPY poetry.* /tmp/pip-tmp/
COPY pyproject.toml /tmp/pip-tmp/
RUN cd /tmp/pip-tmp/ && /home/vscode/.local/bin/poetry install --no-root
RUN npm install -g @devcontainers/cli@v0.30.0