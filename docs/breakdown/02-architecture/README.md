---
title: Architecture
summary: The module map, the single interface reduction, and the determinism rules behind every artifact.
---

# Architecture

How the package is divided, which module owns the variable set, and why two runs
produce the same bytes.

## Contents

<!-- pb:index:start -->
<!-- GENERATED FILE — do not edit. Regenerate with pb-registers. -->
- **INFO-002** [Module map](module-map.md) — Seven modules behind one facade; dependency flows sysmlpy to pycps_sysml2 to pyfmi_sysml2 to pyssp_standard.fmi2, never through pyssp_sysml2.
- **INFO-003** [Interface reduction](interface-reduction.md) — interface.py turns an architecture into Component, PortGroup, Field, and Variable objects, assigns value references once, and is the only place that decides which variables exist.
- **INFO-004** [Determinism model](determinism.md) — A uuid5 guid from a frozen namespace string, an injected clock, and an epoch-stamped sorted archive make every artifact reproducible.
<!-- pb:index:end -->
