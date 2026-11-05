# Case: `controller`

A component with a list parameter, a String parameter, a three-field input, and
two mixed-type outputs.

## Artifacts

| Path | Kind |
| --- | --- |
| `Controller/modelDescription.xml` | Golden, FMI 2.0 CoSimulation model description |

Input: `tests/fixtures/controller/controller.sysml` (`ControllerComposition`).
The input is not duplicated here; the fixture is the single source of the
architecture.

## What this case proves

Every reduction rule is visible in one file: a fixed-length list parameter
expands to `gains[0]` and `gains[1]` with zero-based value references and
one-based output indices; a String parameter carries `start="nominal"` verbatim
while a Real parameter carries `start="1"` and `start="2.5"` produced by the FMI
text formatter; inputs keep `Real`/`Integer` types; the two output ports expand
to `throttle.demand`, `throttle.enabled`, and `status.code`; and
`ModelStructure` lists indices `7 8 9` under both `Outputs` and
`InitialUnknowns`, exactly as v0.3.0 did. The `guid` is pinned in the test
independent of the generator.

- **Conversion:** SysML v2 text → `pyfmi_sysml2.interface` reduction → FMI 2.0
  document dataclasses → `modelDescription.xml`.
- **Requirement / fault:** list expansion, FMI start text, value-reference
  order, and the output indices must not drift; a `[1]`-suffixed list, a
  `start="True"`, or a missing initial unknown is a fault.
- **Level:** component (a generated artifact is the unit under test).
- **Input:** `tests/fixtures/controller/controller.sysml`.
- **Expected:** `Controller/modelDescription.xml`, byte for byte.
- **Independent oracle:** `pyssp_standard` FMI2 XSD plus its semantic validator,
  the independent `Fmi2ModelDescriptionXmlCodec` parser, and a `uuid5` computed
  in the test from the frozen namespace string.
- **Comparison:** exact bytes; the full variable summary is asserted separately
  in `tests/test_model_description.py`.
- **Normalization:** none. The generation time is frozen at
  `2026-01-01T00:00:00Z` by the test.
- **Volatile fields:** `generationDateAndTime` only, fixed by the injected
  clock. The `guid` is deterministic.
- **Update policy:** regenerate only with `UPDATE_GOLDENS=1` and review the
  diff; never in CI, which the test refuses.
- **Notes:** `gains` is authored as `Real[2]` with defaults `(1.0, 2.5)`; the
  applied-set path is covered by a temporary architecture in the test, not by
  this fixture.

## Update history

| Date | Change | Reason |
| --- | --- | --- |
| 2026-11-05 | Created | U3.2: first committed `modelDescription.xml` goldens. |
