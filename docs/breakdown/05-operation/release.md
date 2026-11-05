---
id: INFO-011
type: info
title: Release process
summary: Tag v0.1.0 after a green matrix, build wheel and sdist, install the wheel into a clean venv, and attach the artifacts to the GitHub release.
date: 2026-11-05
status: current
---

# Release process

The version is single-sourced: `pyfmi_sysml2.__version__` in
`src/pyfmi_sysml2/__init__.py`, read by `setuptools` through
`dynamic = ["version"]`.

Steps:

1. Confirm `main` is green on 3.11 and 3.12 and the tree is clean.
2. Set `__version__` to the release version and commit.
3. Tag `v<version>` and push the tag.
4. `wheels.yml` builds `python -m build --wheel --sdist`, asserts exactly one
   wheel and no `0.0.0`, checks the tag against the imported `__version__`,
   uploads `dist/`, and creates the GitHub release with
   `fail_on_unmatched_files: true`.
5. Install the built wheel into a clean virtual environment and run the
   fixture end-to-end path from the installed package, not the source tree.

The dependencies are direct-URL wheels pinned to sibling releases
(`pycps-sysml2` v0.1.0 and `experimental-pyssp-standard` v0.9.2.dev0). A wheel
is installable only when both release assets exist; a tag that points at a
missing asset is not a release.

v0.1.0 is the first release. `pyssp_sysml2 generate fmi` was removed in that
project's v0.4.0; `pyfmi` replaces it.
