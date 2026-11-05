---
id: INFO-013
type: info
title: Roadmap after v0.1.0
summary: v0.2.0 adds FMI authoring attributes through pycps_sysml2 v0.2.0, a Modelica wrapper, and units; the v0.1.0 non-goals stay out of scope.
date: 2026-11-05
status: current
---

# Roadmap after v0.1.0

v0.2.0, in order of dependency:

1. **FMI authoring attributes**, through `pycps_sysml2` v0.2.0. The dialect must
   define guid policy, modelName override, capabilities flags, units, and
   declared variability/initial before this library can emit them. Until then
   the derived defaults are the contract, not a placeholder to patch locally.
2. **Units**, as part of the same attribute work: `UnitDefinitions`,
   `TypeDefinitions`, and per-variable `unit` references.
3. **Modelica wrapper emission**, around a compiled FMU: a block with the
   connector set, parameter defaults, and a call to the FMI functions. This is
   a separate artifact from the current connector package.

Explicit non-goals for the next release as well:

- FMI Model Exchange and FMI 3.0;
- non-`linux64` binaries;
- full C runtime generation (the FMI function skeleton) rather than headers;
- reading or writing SSP/SSD/SSV/SSM, which stays in `pyssp_sysml2`.

A candidate is selected only when the dialect side exists. Adding a control
attribute in this repository without `pycps_sysml2` support would fork the
dialect, which the intent refuses.
