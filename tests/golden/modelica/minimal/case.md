# Case: `modelica/minimal`

The smallest architecture that still exercises both directions: one input and one
output share a single port definition, so the connector has to stay undirected.

- **Conversion:** `minimal.sysml` (SysML v2) → `GeneratedInterfaces/package.mo`,
  `GeneratedInterfaces/package.order`, `GeneratedInterfaces/Interfaces.mo`,
  `GeneratedInterfaces/GeneratedInterfaces.mo`
- **Requirement / fault:** the Modelica connector set must mirror the FMI port
  reduction, and the package must be self-contained and loadable. A missing
  `package.order` entry, a dropped connector, or an embedding of the draft's
  draft's hard-coded package name breaks import in a Modelica tool without any
  test noticing unless the text is pinned.
- **Level:** component
- **Input:** `tests/fixtures/minimal/minimal.sysml` (package `Minimal`,
  composition `Root`); no external source, no licence obligation
- **Expected:** the committed files listed under *Artifacts*
- **Independent oracle:** `omc`, the OpenModelica compiler — `loadFile` on
  `package.mo` plus `checkModel` on both subpackages. This case was verified with
  `OpenModelica 1.26.1` (`/usr/bin/omc`). The generator is this repository; the
  parser and checker are not.
- **Comparison:** exact bytes against the committed file, plus the `omc` gate in
  `tests/test_modelica.py::test_openmodelica_accepts_the_generated_packages`
- **Normalization:** none; the writer is a pure function of the parsed
  architecture and its arguments, with no clock, hash seed, or environment input
- **Volatile fields:** none
- **Update policy:** `UPDATE_GOLDENS=1`, read the diff, commit fixtures and
  goldens together; refused when `CI` is set
- **Notes:** `Signal` is used as `u` (`in`) and `y` (`out`), so no direction
  prefix is emitted — a connector that claims one direction would be wrong for
  the other user. The `omc` gate is marked `slow` (about 2 s for all four
  fixtures in one invocation); the text golden above is the default CI gate.

## Artifacts

Generated from `tests/fixtures/minimal/minimal.sysml`; every artifact path is
relative to this directory.

| Path | Kind |
| --- | --- |
| `GeneratedInterfaces/package.mo` | root package with the `Modelica` uses annotation |
| `GeneratedInterfaces/package.order` | `Interfaces`, `GeneratedInterfaces` |
| `GeneratedInterfaces/Interfaces.mo` | eight primitive input/output connector aliases |
| `GeneratedInterfaces/GeneratedInterfaces.mo` | one connector per port definition |

`case.md` is provenance, not a golden.

## What this case proves

If this case is deleted, a regression that gives an ambiguous connector a
direction, or that drops the `package.order` entry, still passes the controller
and bus cases: those never use one definition in two directions, and the order
file is identical everywhere. This is the only case where a single definition
must remain undirected while its users are `in` and `out`.

## Update history

| Date | Change | Reason |
| --- | --- | --- |
| 2026-11-05 | Case added with the generator | U3.4: Modelica interface package |
