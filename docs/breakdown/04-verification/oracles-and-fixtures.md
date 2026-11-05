---
id: TEST-003
type: test
title: Oracles, fixtures, and goldens
summary: gcc and g++ syntax-check the headers, omc checkModel proves the Modelica package, and four shared fixtures carry case records and byte-compared goldens.
date: 2026-11-05
status: current
---

# Oracles, fixtures, and goldens

External oracles, with the versions recorded on this machine:

- `gcc 13.4.0` — `-std=c11 -fsyntax-only` on the common header;
- `g++ 13.4.0` — `-std=c++17 -fsyntax-only` on the instance helper;
- `omc OpenModelica 1.26.1` — `loadFile` plus `checkModel` on both generated
  subpackages, marked slow and skipped when `omc` is absent.

The compiler tests skip with a reason when the compiler is missing; they do not
silently pass. The omc test asserts zero `Error` text and two successful
`checkModel` calls per fixture.

Fixtures live in `tests/fixtures/<subject>/<subject>.sysml` and are the shared
architectures the goldens are built from:

- `minimal` — one component, scalar parameters and ports;
- `sensor` — String and Boolean fields, list expansion;
- `controller` — parameters, `inout` and mixed directions, array parameters;
- `bus` — a second composition shape and shared port definitions.

Every fixture directory carries a `case.md` with Conversion, Requirement /
fault, Level, Input, Expected, Independent oracle, Comparison, Normalization,
Volatile fields, Update policy, and Notes. Goldens live under
`tests/golden/<artifact>/<subject>/`.

Policy: no architecture-specific name from the source project may appear in
`src/` or in a golden (`Aircraft`, `FuelSystem`, `FlightGearBridge`); a test
enforces the ban. Names are configuration, not constants.
