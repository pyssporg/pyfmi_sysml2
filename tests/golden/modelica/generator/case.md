# Case: `modelica/generator`

A direct FMU model with one output payload: the connector set is built from the
exported component itself, not from a container's leaves.

## Artifacts

Generated from `tests/fixtures/generator/generator.sysml`; every artifact path
is relative to this directory.

| Path | Kind |
| --- | --- |
| `GeneratedInterfaces/package.mo` | root package with the `Modelica` uses annotation |
| `GeneratedInterfaces/package.order` | `Interfaces`, `GeneratedInterfaces` |
| `GeneratedInterfaces/Interfaces.mo` | eight primitive input/output connector aliases |
| `GeneratedInterfaces/GeneratedInterfaces.mo` | one connector per port definition |

`case.md` is provenance, not a golden.

## What this case proves

- **Conversion:** `generator.sysml` (SysML v2) → the four Modelica package
  files under `GeneratedInterfaces/`.
- **Requirement / fault:** the direct export must contribute its own output
  port to the connector set, and the parameter interface must not leak into it;
  a missing `RealSignal` connector or a parameter connector is a fault.
- **Level:** component.
- **Input:** `tests/fixtures/generator/generator.sysml` (package `Generator`,
  definition `Generator`); synthetic and self-contained.
- **Expected:** the committed files listed under *Artifacts*.
- **Independent oracle:** `omc`, the OpenModelica compiler — `loadFile` on
  `package.mo` plus `checkModel` on both subpackages; the generator and the
  fixture are this repository, the parser and checker are not.
- **Comparison:** exact bytes against the committed files, plus the `omc` gate
  in `tests/test_modelica.py::test_openmodelica_accepts_the_generated_packages`.
- **Normalization:** none; the writer is a pure function of the parsed
  architecture and its arguments.
- **Volatile fields:** none.
- **Update policy:** `UPDATE_GOLDENS=1`, read the diff, commit fixture and
  goldens together; refused when `CI` is set.
- **Notes:** `GeneratorParameters :> ParameterInterface` is a parameter port and
  is excluded, leaving only `RealSignal`; the only usage is `out`, so the
  connector carries `output`.

## Update history

| Date | Change | Reason |
| --- | --- | --- |
| 2026-11-05 | Case added with the direct `FmuModel` fixture | Modelica coverage for the direct export pattern. |
