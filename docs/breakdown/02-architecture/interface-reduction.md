---
id: INFO-003
type: info
title: Interface reduction
summary: interface.py turns an architecture into Component, PortGroup, Field, and Variable objects, assigns value references once, and is the only place that decides which variables exist.
date: 2026-11-05
status: current
---

# Interface reduction

`interface.py` is the single source of the variable set. `components()` resolves
the composition root, validates the parameter dialect, and returns exported leaf
components sorted by name. Each `Component` carries parameter fields, port
groups, and the flat `variables` tuple every generator iterates.

The four frozen dataclasses:

- `Field`: a declared member, scalar or fixed-length array, with `members()`
  yielding `(suffix, member_expression)` per element.
- `Variable`: one ScalarVariable — name, type, causality, variability, VR,
  1-based `index`, description, start, and the C member expression.
- `PortGroup`: one port usage with its definition, direction, causality, fields,
  and the Modelica qualifier.
- `Component`: a leaf definition with its complete interface and `outputs`.

Rules encoded here, not repeated in the generators:

- parameters first, then ports in declaration order, fields in declaration
  order, one VR per scalar, restarting at 0 per component;
- `direction_causality()` maps `out` to output and everything else to input;
- `_fixed_count()` refuses a multiplicity that FMI cannot express as scalars;
- a flat connector control is an explicit refusal, not a silent change;
- C, C++, DataType, and Modelica type tables live here, so the four artifacts
  cannot disagree about a primitive's spelling.

`resolve_system()` picks the composition when one part definition has parts and
is not used as a part elsewhere; several candidates require `composition=`.
