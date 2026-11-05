# Case: c-headers/sensor

## Artifacts

- `Sensor_InterfaceCommon.h`
- `Sensor_Tank.h`

**Conversion**: SysML v2 architecture -> C11 interface headers
**Requirement / fault**: U3.3; a Boolean output field and two scalar parameters
must survive the C spelling unchanged
**Level**: component
**Input**: `tests/fixtures/sensor/sensor.sysml`
**Expected**: `Sensor_LevelState` carries `double remaining`, `double fraction`
and `bool empty`; `Sensor_Tank_Instance` defaults `capacity = 3160` and
`reserve = 0.08`; every `level.*` assignment is non-writable
**Independent oracle**: `gcc -std=c11 -fsyntax-only` and
`g++ -std=c++17 -fsyntax-only`, plus the value-reference and causality checks
against `Component.variables`
**Comparison**: byte-for-byte against the golden text
**Normalization**: none
**Volatile fields**: none
**Update policy**: `UPDATE_GOLDENS=1 ./venv/bin/python -m pytest
tests/test_c_headers.py`; never under `CI`
**Notes**: covers `Boolean` in both the C struct and the `SENSOR_DATA_BOOLEAN`
mapping tag

## What this case proves

That non-Real primitives keep their C type in the payload struct and their tag
in the value-reference mapping, and that a two-parameter default survives
formatting.

## Update history

- 2026-11-05 — Initial golden, U3.3.
