# Case: `sensor`

A storage-tank component with two real interface parameters and a Boolean
output field.

## Artifacts

| Path | Kind |
| --- | --- |
| `Tank/modelDescription.xml` | Golden, FMI 2.0 CoSimulation model description |

Input: `tests/fixtures/sensor/sensor.sysml` (`SensorComposition`). The input is
not duplicated here; the fixture is the single source of the architecture.

## What this case proves

Parameter defaults survive the reduction as FMI text at the authored precision
(`capacity` → `3160`, `reserve` → `0.08`, not `0.080000`), so a value authored
in the SysML source reaches the artifact unchanged. Port payloads are named
`<port>.<field>`, the output port expands to three scalar variables in field
declaration order, and the Boolean field carries its `Boolean` type with no
invented start value. `guid` and `modelName="SensorComposition.Tank"` extend
the identity contract to a second composition name.

- **Conversion:** SysML v2 text → `pyfmi_sysml2.interface` reduction → FMI 2.0
  document dataclasses → `modelDescription.xml`.
- **Requirement / fault:** a parameter default must reach the artifact as the
  interface declares it, and one output port must expand to one scalar variable
  per payload field; a rounded default or a collapsed port is a fault.
- **Level:** component (a generated artifact is the unit under test).
- **Input:** `tests/fixtures/sensor/sensor.sysml`.
- **Expected:** `Tank/modelDescription.xml`, byte for byte.
- **Independent oracle:** `pyssp_standard` FMI2 XSD plus its semantic validator,
  and the independent `Fmi2ModelDescriptionXmlCodec` parser.
- **Comparison:** exact bytes; parsed fields are asserted separately in
  `tests/test_model_description.py`.
- **Normalization:** none. The generation time is frozen at
  `2026-01-01T00:00:00Z` by the test.
- **Volatile fields:** `generationDateAndTime` only, fixed by the injected
  clock. The `guid` is deterministic.
- **Update policy:** regenerate only with `UPDATE_GOLDENS=1` and review the
  diff; never in CI, which the test refuses.
- **Notes:** the Boolean output has no start value because the interface
  reduction gives port variables no default; only parameters carry one.

## Update history

| Date | Change | Reason |
| --- | --- | --- |
| 2026-11-05 | Created | U3.2: first committed `modelDescription.xml` goldens. |
