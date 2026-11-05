---
id: INFO-010
type: info
title: pyssp_standard API facts
summary: The codec returns str, interface type and capabilities are both required, Boolean starts are text, ModelStructure indexes are 1-based, and package_archive normalizes modes and epoch.
date: 2026-11-05
status: current
---

# pyssp_standard API facts

These behaviours are relied on; a change in `pyssp_standard` shows up here
first.

- `Fmi2ModelDescriptionXmlCodec.serialize(document)` returns a `str`, not
  bytes. Write it with `encoding="utf-8"`; parse with `codec.parse(text)`.
- `Fmi2ModelDescriptionDocument` needs both `interface_type` and `capabilities`.
  The codec emits the `CoSimulation` element only when both are present, so
  setting one is a silent omission.
- Scalar `start` values are strings in FMI text form. A Boolean must be
  `"true"`/`"false"`; Python's `str(True)` (`"True"`) is invalid. The reduction
  formats through `pycps_sysml2.core.format_value`.
- `Fmi2ModelStructure` unknown `index` is the 1-based ScalarVariable position,
  not the 0-based `valueReference`. `Variable` carries both for this reason.
- `Fmi2ModelDescriptionValidator.validate(document, xml)` performs semantic and
  XSD checks. Call it before writing; it is not part of `serialize`.
- `pyssp_standard.common.archive.archive.package_archive(directory, output)`
  sorts entries, stamps the FMI epoch (2000-01-01), sets metadata modes `0o644`
  and `binaries/` modes `0o755`, and returns the archive path.
- The `FMU.create` facade cannot carry a `sources/` group; the packager composes
  `stage_fmu` and `package_archive` instead.

The package is installed from a pinned direct-URL wheel
(`experimental-pyssp-standard` v0.9.2.dev0), so these are the API facts of that
build, not of an arbitrary release.
