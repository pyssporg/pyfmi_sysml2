# Case: c-headers/minimal

## Artifacts

- `Minimal_InterfaceCommon.h`
- `Minimal_Scale.h`

**Conversion**: SysML v2 architecture -> C11 interface headers
**Requirement / fault**: U3.3; the smallest legal interface must produce a
C-valid common header and one self-contained component header
**Level**: component
**Input**: `tests/fixtures/minimal/minimal.sysml`
**Expected**: one port payload struct (`Minimal_Signal`), the `Minimal_DataType`
and `Minimal_VrMapping` types, and a `Minimal_Scale_ValueReference` enum with
three entries in value-reference order; the instance struct defaults `gain` to
`2` and declares `u` and `y` as `Minimal_Signal` members
**Independent oracle**: `gcc -std=c11 -fsyntax-only` on the common header and
`g++ -std=c++17 -fsyntax-only` on the instance helper; the value-reference enum
is cross-checked against `Component.variables`
**Comparison**: byte-for-byte against the golden text
**Normalization**: none; the generator reads no clock and sorts components by
name, so the same input always yields the same bytes
**Volatile fields**: none
**Update policy**: `UPDATE_GOLDENS=1 ./venv/bin/python -m pytest
tests/test_c_headers.py`; never under `CI`
**Notes**: one scalar input and one scalar output exercise the output-writable
rule with the smallest possible variable set

## What this case proves

That the common header alone is enough for a C translation unit, and that a
component header compiles in both C11 and C++17 without the C++ block leaking
`nullptr` or brace initializers into C.

## Update history

- 2026-11-05 — Initial golden, U3.3.
