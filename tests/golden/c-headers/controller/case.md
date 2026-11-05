# Case: c-headers/controller

## Artifacts

- `Controller_InterfaceCommon.h`
- `Controller_Controller.h`

**Conversion**: SysML v2 architecture -> C11 interface headers
**Requirement / fault**: U3.3; a fixed-length parameter array, a String
parameter, and a payload field whose name is a C/C++ keyword must all be
emitted as valid C and C++
**Level**: component
**Input**: `tests/fixtures/controller/controller.sysml`
**Expected**: `double gains[2] = {1, 2.5};`, `std::string label = "nominal";`,
one enum entry per element (`..._VR_GAINS_0_`, the frozen sanitizer keeps the
trailing underscore from `gains[0]`), and `double auto_;` because `auto` is a
keyword in both languages
**Independent oracle**: `gcc -std=c11 -fsyntax-only` and
`g++ -std=c++17 -fsyntax-only`; the keyword escape is what makes the second
compile pass, so the compiler is the oracle for it
**Comparison**: byte-for-byte against the golden text
**Normalization**: none; the keyword escape is deterministic and part of the
emitted format
**Volatile fields**: none
**Update policy**: `UPDATE_GOLDENS=1 ./venv/bin/python -m pytest
tests/test_c_headers.py`; never under `CI`
**Notes**: the SysML field stays `auto`; only the member spelling becomes
`auto_`, and the VR entry still names `COMMAND_AUTO`

## What this case proves

That arrays expand element-wise in both the enum and the member default, that
`String` becomes `const char*` in the payload struct and `std::string` in the
instance, and that reserved words are escaped instead of producing a header the
compiler rejects.

## Update history

- 2026-11-05 — Initial golden, U3.3.
