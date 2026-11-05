---
id: CP-002
type: capability
title: Variable model
summary: Parameters come from the parameter dialect, lists expand into scalars, port fields are dotted names, and value references restart at zero per component.
date: 2026-11-05
status: current
---

# Variable model

The variable set is fixed before any artifact is written. It has two sources.

## Parameters

- Parameters come from the parameter dialect only (`in port parameters ...`).
  A flat parameter attribute is rejected, never silently dropped.
- A parameter keeps its interface default as `start`, with `variability=fixed`
  and `causality=parameter`. An applied parameter set does not override it in
  v0.1.0.
- A fixed-length list expands into one scalar per element, named
  `<name>[<index>]`, zero-based. A non-fixed multiplicity is refused.

## Ports

- A port usage contributes one variable per payload field, named
  `<port>.<field>`; a list field expands to `<port>.<field>[<index>]`.
- `out` becomes `causality="output"`. `in`, `inout`, and an undirected port
  become `causality="input"`, because FMI 2.0 has no bidirectional scalar.
- Parameters ports and control attributes are not signal fields.
- A port definition that sets the flat-connector control is refused in v0.1.0
  rather than flattened.

## Ordering and identity

- Value references restart at 0 for every component: parameters first, then
  ports in declaration order, then fields in declaration order.
- Components are exported sorted by name; each component is independent, so
  its headers and modelDescription agree on the same numbered set.
- One scalar per variable: FMI 2.0 has no array variable.
