# Case: `modelica/controller`

Mixed primitives on both sides: an `input Integer` field and an
`output Boolean` field in the same package.

- **Conversion:** `controller.sysml` (SysML v2) → `GeneratedInterfaces/package.mo`,
  `GeneratedInterfaces/package.order`, `GeneratedInterfaces/Interfaces.mo`,
  `GeneratedInterfaces/GeneratedInterfaces.mo`
- **Requirement / fault:** the connector member type must be the FMI primitive,
  not a stringified SysML type, and the direction must come from the port usage.
  A generator that emits `Real` for every member, or that drops the `out` prefix
  on `Throttle`, produces a package that still loads — the fault only shows up
  when a tool wires the connector.
- **Level:** component
- **Input:** `tests/fixtures/controller/controller.sysml` (package `Controller`,
  composition `ControllerComposition`); no external source, no licence obligation
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
- **Notes:** the parameter port (`ControllerParameters`, with a `Real[2]` and a
  `String`) is not a signal port and correctly produces no connector; parameter
  interface ports reach the artefacts through the FMI reduction, not here. The
  `omc` gate is marked `slow` (about 2 s for all four fixtures in one
  invocation); the text golden above is the default CI gate.

## Artifacts

Generated from `tests/fixtures/controller/controller.sysml`; every artifact path
is relative to this directory.

| Path | Kind |
| --- | --- |
| `GeneratedInterfaces/package.mo` | root package with the `Modelica` uses annotation |
| `GeneratedInterfaces/package.order` | `Interfaces`, `GeneratedInterfaces` |
| `GeneratedInterfaces/Interfaces.mo` | eight primitive input/output connector aliases |
| `GeneratedInterfaces/GeneratedInterfaces.mo` | one connector per port definition |

`case.md` is provenance, not a golden.

## What this case proves

If this case is deleted, a regression that flattens every member to `Real`, or
that loses the `input `/`output ` prefix on a single-direction connector, still
passes the minimal and sensor cases only if those happen to carry the same type
mix — they do not: neither has an `output Integer`. This is the case that keeps
the primitive-type mapping and the prefix together.

## Update history

| Date | Change | Reason |
| --- | --- | --- |
| 2026-11-05 | Case added with the generator | U3.4: Modelica interface package |
