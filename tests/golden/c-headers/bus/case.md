# Case: c-headers/bus

## Artifacts

- `Bus_InterfaceCommon.h`
- `Bus_Bus.h`

**Conversion**: SysML v2 architecture -> C11 interface headers
**Requirement / fault**: U3.3; a component with no parameters, seven ports that
reuse four payload definitions, and `inout`/undirected directions must not
duplicate a port struct or lose a value reference
**Level**: component
**Input**: `tests/fixtures/bus/bus.sysml`
**Expected**: exactly four payload structs (`Bus_Actuation`, `Bus_Orientation`,
`Bus_Position`, `Bus_StatusPacket`) although `Orientation` is used three times;
twenty enum entries in value-reference order; every `shared.*` entry writable
because `inout` is an input in FMI 2.0
**Independent oracle**: `gcc -std=c11 -fsyntax-only` and
`g++ -std=c++17 -fsyntax-only`, plus the value-reference order check against
`Component.variables`
**Comparison**: byte-for-byte against the golden text
**Normalization**: none; first-use order is fixed by the sorted component list
and each component's declaration order
**Volatile fields**: none
**Update policy**: `UPDATE_GOLDENS=1 ./venv/bin/python -m pytest
tests/test_c_headers.py`; never under `CI`
**Notes**: largest fixture; catches duplicate struct emission and the
`inout`-as-input rule

## What this case proves

That port definitions are emitted once in first-use order, and that a
twenty-variable component keeps enum order identical to the IR value
references.

## Update history

- 2026-11-05 — Initial golden, U3.3.
