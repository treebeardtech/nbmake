
## Developing

nbmake uses devcontainers to pre-configure a dev environment. We recommend you open the project in vscode with the remote containers extension to contribute.

For non-vscode users, here are some install steps:

### Run static checks
```
pre-commit run --all-files
pre-commit install
```

### Run tests
```
pytest
```
