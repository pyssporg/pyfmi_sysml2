---
id: TEST-001
type: test
title: Test strategy
summary: Six pytest markers, five levels plus a slow qualifier; each owns a distinct fault class, and component goldens are the default gate.
date: 2026-11-05
status: current
---

# Test strategy

The suite is organized by the question a test answers, not by module. The six
markers are declared in `pyproject.toml`:

- **static** — a rule that holds without running the package: layering,
  dependency shape, fixture records, provenance (`test_layering.py`,
  `test_fixture_policy.py`).
- **unit** — one object's behaviour, no artifact written. The reduction is
  asserted through `pyfmi_sysml2.interface` inside the artifact tests until a
  dedicated `test_interface.py` exists.
- **component** — a generated artifact is the unit under test: the bytes of
  modelDescription, a header, a Modelica package, or a packed `.fmu`, compared
  against its golden.
- **contract** — two directions must agree: VR order between XML and header,
  connector set against FMI variables, and one component identity across XML,
  header, and archive (`test_cross_artifact.py`).
- **system** — the CLI end to end: parsing, exit codes, files written by one
  `pyfmi` invocation (`test_cli.py`).
- **slow** — not a level but an orthogonal qualifier that keeps the `omc` check
  out of the default subset.

Default gate: `python -m pytest -m "not slow"`. CI runs exactly that on 3.11 and
3.12, plus `ruff check src tests`, and fails if the checkout is dirty afterwards.

Goldens are compared byte-for-byte. `UPDATE_GOLDENS=1` rewrites them locally,
but never when `CI` is set: a golden is a reviewed artifact, not test output.
`tests/README.md` maps each marker to its files and the fault it can see.
