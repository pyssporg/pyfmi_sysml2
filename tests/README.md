# Tests

Six levels. Each level owns a fault the others cannot see, so a green run at a
lower level is not evidence for a higher one.

| Marker | Level | What it can fail on | Where |
| --- | --- | --- | --- |
| `static` | source and repository policy | a rule that holds without running the package: layering, dependency shape, fixture records, golden coverage, provenance | `test_fixture_policy.py`, `test_layering.py` |
| `unit` | one object's behaviour | the reduction from a parsed architecture to variables: identifiers, defaults, variable order; no artifact written | asserted through `pyfmi_sysml2.interface` inside the artifact tests until a dedicated `test_interface.py` exists |
| `component` | one generated artifact | the bytes of `modelDescription.xml`, a C header, a Modelica package, a packaged `.fmu` — compared against its golden | `test_model_description.py`, `test_c_headers.py`, `test_modelica.py`, `test_package.py` |
| `contract` | two directions must agree | value-reference order between the XML and the C enum, the Modelica connector set against the FMI variables, and one component identity across XML, header, and archive | `test_cross_artifact.py`, recorded by `tests/golden/cross-artifact/case.md` |
| `system` | the CLI end to end | argument parsing, exit codes, files written by one `pyfmi` invocation | `test_cli.py` |
| `slow` | runtime qualifier | a check too expensive for the default run, such as the `omc` compile gate; combined with the level above, excluded with `-m "not slow"` | `test_modelica.py` |

`slow` is not a level of its own: it is an orthogonal marker that keeps an
expensive check out of the default subset.

```bash
./venv/bin/python -m pytest tests/                  # everything, slow included
./venv/bin/python -m pytest tests/ -m "not slow"    # the CI subset
./venv/bin/python -m pytest tests/ -m static        # policy only
```

## Where the evidence lives

- `tests/fixtures/<subject>/` — the architecture inputs. A fixture is the only
  input a golden has, so it is reviewed like a golden; see
  `tests/fixtures/README.md`.
- `tests/golden/<artifact>/<subject>/` — committed expected output, compared
  **byte for byte** by `tests/golden_utils.py`. A golden is not test output; it
  is a reviewed artifact.
- `case.md` — the record next to each fixture and each golden. It states the
  conversion, the requirement or fault the case guards, the level, the input,
  the expected bytes, the *independent* oracle, the comparison, what may be
  normalized, the volatile fields, the update policy, and the update history.
  Every golden is named by a backticked path in the record that governs it.

An artifact test that only asserts "a file was written" is not evidence; the
fault must be visible in a trajectory, a compiled header, a validated document,
or a byte diff.

## Regenerating goldens

Goldens are regenerated deliberately, never as a side effect of running the
suite:

```bash
UPDATE_GOLDENS=1 ./venv/bin/python -m pytest tests/test_c_headers.py
git diff tests/golden/        # read every line before committing
```

The rewrite is refused whenever `CI` is set: `conftest.update_goldens()` returns
`False` under `CI` regardless of `UPDATE_GOLDENS`, so CI can only compare. A
golden updated in CI would make the gate agree with whatever the code did.

Committing a fixture change and the goldens it moves happens in one commit, with
the `case.md` update history extended.
