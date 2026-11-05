---
id: INFO-006
type: info
title: C header generation
summary: One plain-C common header per architecture plus one header per component with a VR enum, VrCount, a C++ Instance, and initialize_vr_map.
date: 2026-11-05
status: current
---

# C header generation

`generate_c_headers()` writes `<prefix>_InterfaceCommon.h` followed by one
`<prefix>_<Component>.h` per exported component. `prefix` defaults to the
architecture package name. A direct FMU model whose definition carries the
package name uses that name once (`Generator.h`, not `Generator_Generator.h`);
`header_stem()` owns the rule for both the file name and the C identifiers.

Common header:

- include guard, `stdbool.h`/`stddef.h`/`stdint.h`;
- one `typedef struct <prefix>_<PortDefinition>` per distinct port definition
  in first-use order, fields in declaration order;
- a `<prefix>_DataType` enum (`NONE`, `REAL`, `INTEGER`, `BOOLEAN`, `STRING`);
- `<prefix>_VrMapping` (`void* data`, `DataType type`, `bool writable`) in
  plain C, so a C simulator can read the mapping a C++ host fills in.

Component header:

- `<PREFIX>_<COMPONENT>_VR_<VARIABLE> = <vr>` for every variable;
- `VrCount`;
- inside `#ifdef __cplusplus`, a `<prefix>_<Component>_Instance` struct holding
  `vr_map[]`, parameter defaults, and one payload struct per port, plus
  `initialize_vr_map()`.

Details that are deliberate:

- output variables map with `writable=false`; parameters and inputs map `true`;
- C and C++ keywords are escaped with a trailing underscore on the struct member
  only (`auto` becomes `auto_`); FMI names are untouched;
- arrays are fixed-size members, matching the expanded scalar variables;
- string defaults are C-escaped and quoted.

The common header is valid C11; only the instance helper needs C++17. Both are
compiled with `-fsyntax-only` in the test suite.
