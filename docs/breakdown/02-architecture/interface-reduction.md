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
the export unit, validates the parameter dialect, and returns the exported
components. A container root exports its leaf descendants sorted by name; a
part definition marked `:> FmuModel` is itself the export unit and returns as
the single component. Each `Component` carries parameter fields, port groups,
and the flat `variables` tuple every generator iterates.

The four interface dataclasses:

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

`resolve_system()` picks a part definition marked `:> FmuModel` as the export
unit; several marked definitions require `composition=` and are refused by
name. When none is marked, it picks the part definition that has parts and is
not used as a part elsewhere; several such roots also require `composition=`.

`export_identity()` owns the naming rule for the selected unit: a container
root names a component `<system>.<component>`, while a direct FMU model uses
the bare definition name. The modelDescription and the guid both read that one
helper, so a direct FMU cannot become `Generator.Generator`.
