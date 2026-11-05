# Case: `generator`

A direct FMU model: the definition is the component, with no container root.

## Artifacts

| Path | Kind |
| --- | --- |
| `Generator/modelDescription.xml` | Golden, FMI 2.0 CoSimulation model description |

Input: `tests/fixtures/generator/generator.sysml` (`Generator`). The input is
not duplicated here; the fixture is the single source of the architecture.

## What this case proves

That the marked definition is its own export unit: `modelName` and
`modelIdentifier` are both `Generator` rather than `Generator.Generator`, the
`guid` is `uuid5(NAMESPACE_URL, "pyssp_sysml2/Generator")`, and the two
parameters keep their authored defaults while the single output stays in
`ModelStructure`.

- **Conversion:** SysML v2 text → `pyfmi_sysml2.interface` reduction → FMI 2.0
  document dataclasses → `modelDescription.xml`.
- **Requirement / fault:** a rebuild with the same architecture and generation
  time must reproduce the same bytes, and the file must pass XSD and semantic
  validation; a doubled identity or a lost default is a fault.
- **Level:** component (a generated artifact is the unit under test).
- **Input:** `tests/fixtures/generator/generator.sysml`.
- **Expected:** `Generator/modelDescription.xml`, byte for byte.
- **Independent oracle:** `pyssp_standard` FMI2 XSD plus its semantic validator,
  and the independent `Fmi2ModelDescriptionXmlCodec` parser.
- **Comparison:** exact bytes; parsed fields are asserted separately in
  `tests/test_model_description.py`.
- **Normalization:** none. The generation time is frozen at
  `2026-01-01T00:00:00Z` by the test, so the golden has no wall-clock input.
- **Volatile fields:** `generationDateAndTime` only, fixed by the injected
  clock. The `guid` is deterministic from the definition name.
- **Update policy:** regenerate only with `UPDATE_GOLDENS=1` and review the
  diff; never in CI, which the test refuses.
- **Notes:** the fixture authors `fmu_meta`, which is authoring data and does
  not appear in the variable set or the document.

## Update history

| Date | Change | Reason |
| --- | --- | --- |
| 2026-11-05 | Created | Direct `FmuModel` identity golden. |
