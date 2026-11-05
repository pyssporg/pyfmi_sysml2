# Case: `bus`

A wide component with no parameters, six ports, and an inout plus an undirected
port.

## Artifacts

| Path | Kind |
| --- | --- |
| `Bus/modelDescription.xml` | Golden, FMI 2.0 CoSimulation model description |

Input: `tests/fixtures/bus/bus.sysml` (`BusComposition`). The input is not
duplicated here; the fixture is the single source of the architecture.

## What this case proves

Twenty scalar variables with value references `0..19` and output indices
`13..20` exercise the ordering bounds and the causalities the narrow fixtures do
not reach. The `inout` port and the undirected port both become inputs, because
FMI 2.0 has no bidirectional scalar variable, so `shared` appears as an input
and no variable is silently dropped. A component with no parameter interface
emits no `parameter`/`fixed` variables at all.

- **Conversion:** SysML v2 text → `pyfmi_sysml2.interface` reduction → FMI 2.0
  document dataclasses → `modelDescription.xml`.
- **Requirement / fault:** every port field must appear exactly once, in
  declaration order, with the direction degraded to an input where FMI cannot
  express it; a dropped `inout` field or a reordered value reference is a
  fault.
- **Level:** component (a generated artifact is the unit under test).
- **Input:** `tests/fixtures/bus/bus.sysml`.
- **Expected:** `Bus/modelDescription.xml`, byte for byte.
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
- **Notes:** `variableNamingConvention="structured"` is what makes the dotted
  port field names legal FMI 2.0 names.

## Update history

| Date | Change | Reason |
| --- | --- | --- |
| 2026-11-05 | Created | U3.2: first committed `modelDescription.xml` goldens. |
