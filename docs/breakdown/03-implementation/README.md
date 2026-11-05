---
title: Implementation
summary: Per-module notes and the pyssp_standard and pycps_sysml2 API facts the code depends on.
---

# Implementation

What each module does, and the library behaviours it relies on.

## Contents

<!-- pb:index:start -->
<!-- GENERATED FILE — do not edit. Regenerate with pb-registers. -->
- **INFO-005** [modelDescription generation](model-description.md) — model_description.py assembles a pyssp_standard FMI 2 document from the reduction, stamps the clock, serializes, validates, then writes one file per component.
- **INFO-006** [C header generation](c-headers.md) — One plain-C common header per architecture plus one header per component with a VR enum, VrCount, a C++ Instance, and initialize_vr_map.
- **INFO-007** [Modelica generation](modelica.md) — generate_modelica writes a configurable root package with Interfaces and GeneratedInterfaces, one connector per distinct port definition.
- **INFO-008** [FMU packaging](packaging.md) — stage_fmu lays out the FMU tree and validates identifier and platform; package_fmu writes the epoch-stamped sorted zip through package_archive.
- **INFO-009** [CLI](cli.md) — The pyfmi entry point has four subcommands, prints one written path per line, exits 1 on handled model or input errors, and 2 on argument errors.
- **INFO-010** [pyssp_standard API facts](pyssp-standard-api.md) — The codec returns str, interface type and capabilities are both required, Boolean starts are text, ModelStructure indexes are 1-based, and package_archive normalizes modes and epoch.
<!-- pb:index:end -->
