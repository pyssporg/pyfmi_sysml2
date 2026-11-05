---
id: INFO-001
type: info
title: Intent
summary: pyfmi_sysml2 implements the FMI half of a SysML dialect owned by pycps_sysml2, and refuses to become an FMI authoring tool.
date: 2026-11-05
status: current
---

# Intent

## Purpose

`pyfmi_sysml2` turns one SysML v2 architecture into the FMI 2.0 CoSimulation
artifacts a simulation workflow consumes: `modelDescription.xml`, C interface
headers, Modelica connectors, and a packaged `.fmu`. It generates files; it does
not compile models, run simulations, or judge results.

The SysML dialect is not owned here. `pycps_sysml2` is the dialect home: it
parses the model and exposes parameters, ports, controls, and metadata.
`pyfmi_sysml2` implements the FMI half of that contract and nothing else.

## Scope

Belongs here:

- the reduction of an architecture onto one FMI variable set;
- modelDescription, C header, Modelica, and FMU archive generation;
- deterministic bytes from an injected generation time;
- the `pyfmi` command line.

Belongs elsewhere:

- SysML parsing, IR, variation, selection, parameter markers: `pycps_sysml2`;
- FMI XML object model, codec, validator, archive writer: `pyssp_standard`;
- SSP, SSD, SSV, SSM emission and SysML synthesis: `pyssp_sysml2`.

## Commitments

- **The artifact is the library boundary.** Only FMI XML, C headers, Modelica
  text, and the `.fmu` archive cross to another project.
- **One dialect interface.** The SysML dialect is read only through
  `pycps_sysml2`; this package must never import `pyssp_sysml2`.
- **One FMI serializer.** FMI XML is built, serialized, and validated only
  through `pyssp_standard.standard.fmi2`.
- **Reproducibility is a feature.** The same architecture and the same injected
  `generation_time` produce byte-identical files, including the archive.
- **The reduction is the contract.** Every generator reads the variable set
  through one module, so the artifacts cannot disagree about it.

## Non-Goals

- FMI Model Exchange and FMI 3.0.
- Binary platforms other than `linux64`.
- FMI authoring attributes: guid policy, modelName override, capabilities,
  units, declared variability or initial.
- Full C runtime generation or a Modelica wrapper around a compiled FMU; only
  headers, connectors, and the VR mapping are emitted.
- Presenting generated placeholders as a complete FMU implementation.
