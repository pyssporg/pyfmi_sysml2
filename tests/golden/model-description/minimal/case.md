# Case: `minimal`

One leaf component with an interface parameter, one input, and one output.

## Artifacts

| Path | Kind |
| --- | --- |
| `Scale/modelDescription.xml` | Golden, FMI 2.0 CoSimulation model description |

Input: `tests/fixtures/minimal/minimal.sysml` (`Root`). The input is not
duplicated here; the fixture is the single source of the architecture.

## What this case proves

The smallest artifact set the generator must support: a parameter declared in a
parameter interface keeps its authored default as FMI text (`gain` → `2`), the
input and the output keep their value references in declaration order
(parameter, then ports), `CoSimulation` carries `modelIdentifier="Scale"`, and
`ModelStructure` lists the single output both as an output and as an initial
unknown. The `guid` and `modelName="Root.Scale"` pin the identity contract
shared with pyssp_sysml2 v0.3.0.

- **Conversion:** SysML v2 text → `pyfmi_sysml2.interface` reduction → FMI 2.0
  document dataclasses → `modelDescription.xml`.
- **Requirement / fault:** a rebuild with the same architecture and generation
  time must reproduce the same bytes, and the file must pass XSD and semantic
  validation; a lost default or a shifted value reference is a fault.
- **Level:** component (a generated artifact is the unit under test).
- **Input:** `tests/fixtures/minimal/minimal.sysml`.
- **Expected:** `Scale/modelDescription.xml`, byte for byte.
- **Independent oracle:** `pyssp_standard` FMI2 XSD plus its semantic validator,
  and the independent `Fmi2ModelDescriptionXmlCodec` parser.
- **Comparison:** exact bytes; parsed fields are asserted separately in
  `tests/test_model_description.py`.
- **Normalization:** none. The generation time is frozen at
  `2026-01-01T00:00:00Z` by the test, so the golden has no wall-clock input.
- **Volatile fields:** `generationDateAndTime` only, fixed by the injected
  clock. The `guid` is deterministic from the composition and component names.
- **Update policy:** regenerate only with `UPDATE_GOLDENS=1` and review the
  diff; never in CI, which the test refuses.
- **Notes:** no `DefaultExperiment` and no `UnitDefinitions` because the fixture
  authors no control attributes and the dialect has no unit carrier.

## Update history

| Date | Change | Reason |
| --- | --- | --- |
| 2026-11-05 | Created | U3.2: first committed `modelDescription.xml` goldens. |
