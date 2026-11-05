# Case: c-headers/generator

## Artifacts

- `Generator_InterfaceCommon.h`
- `Generator.h`

**Conversion**: SysML v2 architecture -> C11 interface headers
**Requirement / fault**: the direct `:> FmuModel` export must name its one
component after the definition, so the package name is not repeated and the C
type prefix is `Generator`, not `Generator_Generator`; a doubled file or symbol
name is a fault
**Level**: component
**Input**: `tests/fixtures/generator/generator.sysml`
**Expected**: one component header `Generator.h` with a
`Generator_ValueReference` enum of three entries (`GENERATOR_VR_GAIN`,
`GENERATOR_VR_OFFSET`, `GENERATOR_VR_Y_VALUE`), `Generator_VrCount = 3`, and a
`Generator_Instance` whose parameters default to `2` and `0.5`; the common
header carries `Generator_RealSignal`, `Generator_DataType`, and
`Generator_VrMapping`
**Independent oracle**: `gcc -std=c11 -fsyntax-only` on the common header and
`g++ -std=c++17 -fsyntax-only` on the instance helper; the value-reference enum
is cross-checked against `Component.variables`
**Comparison**: byte-for-byte against the golden text
**Normalization**: none; the generator reads no clock and the direct export has
exactly one component
**Volatile fields**: none
**Update policy**: `UPDATE_GOLDENS=1 ./venv/bin/python -m pytest
tests/test_c_headers.py`; never under `CI`
**Notes**: the fixture package and the FMU definition share the name
`Generator`, which is the case the collapse exists for; a container whose
component shares the package name keeps `<Package>_<Component>.h`

## What this case proves

That a direct FMU model names its one component header once, and that the C
symbols, the enum entries, and the C++ instance helper agree with the file name
without a repeated stem.

## Update history

- 2026-11-05 — Initial golden for the direct `FmuModel` export pattern.
