# Case: minimal

The smallest architecture every generator must accept: one parameter, one input,
one output, three scalar variables.

## Artifacts

- `minimal.sysml`

**Conversion**: SysML v2 architecture -> the four FMI 2.0 artifacts
(`modelDescription.xml`, C headers, Modelica package, packaged `.fmu`)
**Requirement / fault**: the floor of the input space; a generator that only
works with a parameter interface, several ports, or a list parameter has no
legal input at all if this case fails
**Level**: unit; the fixture is parsed input, not a generated artifact
**Input**: authored here, no external source
**Expected**: package `Minimal`, part `Scale`, composition `Root`; three scalar
variables in value-reference order `0..2` — parameter `parameters.gain` (default
`2.0`), input `u.value`, output `y.value`; one payload definition (`Signal`) used
by both directions, so the Modelica connector must stay undirected
**Independent oracle**: `pycps_sysml2.load` parses the file, and every golden
derived from it is compared byte-for-byte by `tests/golden_utils.py`
**Comparison**: the goldens under `tests/golden/<subject>/minimal/` are the
comparison, byte-for-byte
**Normalization**: none; the fixture text is the only input and carries no
clock, path, or environment value
**Volatile fields**: none
**Update policy**: change the fixture and every affected golden in one commit;
regenerate with `UPDATE_GOLDENS=1`, never under `CI`
**Notes**: the only case where one payload definition is used as an input and as
an output; `Root.scale` is the single leaf component
**Provenance**: synthetic, authored for this repository; no external source and
no licence obligation

## What this case proves

That the generators have a working floor: no parameters beyond one scalar, no
port wider than one field, no direction ambiguity beyond the shared `Signal`
definition. If this case fails, every wider fixture is meaningless.

## Update history

- 2026-11-05 — Fixture and record created, U3.7.
