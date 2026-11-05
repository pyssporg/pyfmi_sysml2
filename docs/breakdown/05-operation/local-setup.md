---
id: INFO-012
type: info
title: Local setup
summary: Create the venv, install the editable package with the dev extra, and use the repo-local interpreter for every command.
date: 2026-11-05
status: current
---

# Local setup

The repository ships its own `venv` with both dependencies resolved.

```bash
python3 -m venv venv
./venv/bin/pip install -e ".[dev]"
```

The two runtime dependencies are direct-URL wheels, not index lookups:

- `pycps-sysml2` v0.1.0, the SysML dialect;
- `experimental-pyssp-standard` v0.9.2.dev0, the FMI XML and archive API.

They are installed from `github.com/pyssporg/<repo>/releases/download/v<version>/`
assets. An unreleased tag makes the package uninstallable, so bump the pin only
after the sibling wheel exists.

Commands:

```bash
./venv/bin/pyfmi --help
./venv/bin/ruff check src tests
./venv/bin/python -m pytest -m "not slow"
./venv/bin/python -m pytest            # includes the omc oracle
```

`UPDATE_GOLDENS=1 ./venv/bin/python -m pytest` rewrites goldens locally; it has
no effect when `CI` is set. Review the diff before committing a golden.

The editable install provides the `pyfmi` console script. Without it, run
`PYTHONPATH=src ./venv/bin/python -m pyfmi_sysml2.cli`.
