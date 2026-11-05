---
id: INFO-008
type: info
title: FMU packaging
summary: stage_fmu lays out the FMU tree and validates identifier and platform; package_fmu writes the epoch-stamped sorted zip through package_archive.
date: 2026-11-05
status: current
---

# FMU packaging

`stage_fmu(directory, *, model_description, binary, platform="linux64", headers,
resources, documentation, overwrite=False)` writes a clean tree and returns it:

- the modelDescription bytes are copied verbatim to the root;
- the binary goes to `binaries/<platform>/` and gets the executable bit;
- headers go to `sources/`, resources to `resources/`, documentation to
  `documentation/`; directories are copied recursively; empty groups create no
  directory.

Before writing, `stage_fmu` parses the modelDescription once with the FMI codec
and keeps the exact bytes for the copy. It refuses:

- `fmiVersion` other than `2.0`;
- a document without an interface element or `modelIdentifier`;
- a `modelIdentifier` unequal to the binary stem;
- a platform token that is unsafe or outside `SUPPORTED_PLATFORMS` (`linux64`);
- a non-empty staging directory unless `overwrite=True`;
- duplicate file names under one archive folder.

`package_fmu(output, *, model_description, binary, platform="linux64", headers,
resources, documentation, stage_dir=None)` stages into a temporary directory (or
`stage_dir`) and calls `package_archive`, then verifies that
`modelDescription.xml` and `binaries/<platform>/<binary name>` are present.

`pyssp_standard`'s `FMU.create` facade cannot carry a `sources/` group, so the
packager uses `stage_fmu` plus `package_archive` rather than that facade.
