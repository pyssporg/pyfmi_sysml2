---
id: INFO-007
type: info
title: Modelica generation
summary: generate_modelica writes a configurable root package with Interfaces and GeneratedInterfaces, one connector per distinct port definition.
date: 2026-11-05
status: current
---

# Modelica generation

`generate_modelica()` writes four files under `<output>/<package>/`:

- `package.mo` — the root package with the `within` clause and
  `annotation(uses(Modelica(version="4.0.0")))`;
- `package.order` — `Interfaces` then `GeneratedInterfaces`;
- `Interfaces.mo` — `<Type>Input = input <Type>` and `<Type>Output = output
  <Type>` for Real, Integer, Boolean, and String;
- `GeneratedInterfaces.mo` — one `connector` per distinct port definition.

A connector is a type, so its direction must hold for every usage. The member
prefix is `input`/`output` only when all usages agree; if any usage is `inout`,
undirected, or disagrees with another, the connector stays undirected. This is
the Modelica counterpart of the FMI rule that `inout` becomes an input.

Configuration, never constants:

- `package` defaults to `GeneratedInterfaces`;
- `within` nests the generated root inside an existing scope;
- the subpackages are declared inside the parent, so only the root
  `package.mo` carries the bare `within`.

Names are emitted from the architecture; no domain-specific package or connector
name is baked into the generator. Fields keep their FMI type and fixed array
size; a list field is `Type name[n]` in the connector, while the FMI side
expands it into scalars.
