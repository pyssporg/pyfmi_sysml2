# Case: `modelica/sensor`

An `output Boolean` in a multi-field output payload: the case that pins a
non-Real primitive behind an `output` prefix.

- **Conversion:** `sensor.sysml` (SysML v2) → `GeneratedInterfaces/package.mo`,
  `GeneratedInterfaces/package.order`, `GeneratedInterfaces/Interfaces.mo`,
  `GeneratedInterfaces/GeneratedInterfaces.mo`
- **Requirement / fault:** connector members are emitted in the port
  definition's declaration order with their FMI primitive. Reordering members,
  or mapping `Boolean` to `Real`, keeps the package parseable but changes what a
  tool binds on the wire.
- **Level:** component
- **Input:** `tests/fixtures/sensor/sensor.sysml` (package `Sensor`, composition
  `SensorComposition`); no external source, no licence obligation
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
- **Notes:** `LevelState` keeps its declared order (`remaining`, `fraction`,
  `empty`) and `empty` stays `Boolean`. The `omc` gate is marked `slow` (about
  2 s for all four fixtures in one invocation); the text golden above is the
  default CI gate.

## Artifacts

Generated from `tests/fixtures/sensor/sensor.sysml`; every artifact path is
relative to this directory.

| Path | Kind |
| --- | --- |
| `GeneratedInterfaces/package.mo` | root package with the `Modelica` uses annotation |
| `GeneratedInterfaces/package.order` | `Interfaces`, `GeneratedInterfaces` |
| `GeneratedInterfaces/Interfaces.mo` | eight primitive input/output connector aliases |
| `GeneratedInterfaces/GeneratedInterfaces.mo` | one connector per port definition |

`case.md` is provenance, not a golden.

## What this case proves

If this case is deleted, a regression that maps `Boolean` to `Real` in a
connector still passes the bus case only through `StatusPacket`, which has no
`Boolean`; the controller has one, but not inside a multi-field output whose
order also matters. This case pins both together.

## Update history

| Date | Change | Reason |
| --- | --- | --- |
| 2026-11-05 | Case added with the generator | U3.4: Modelica interface package |
