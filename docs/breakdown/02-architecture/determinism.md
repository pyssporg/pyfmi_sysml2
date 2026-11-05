---
id: INFO-004
type: info
title: Determinism model
summary: A uuid5 guid from a frozen namespace string, an injected clock, and an epoch-stamped sorted archive make every artifact reproducible.
date: 2026-11-05
status: current
---

# Determinism model

Three inputs could otherwise vary between runs. Each is pinned.

## Guid

`component_guid()` is `uuid5(NAMESPACE_URL, "pyssp_sysml2/<composition>/<component>")`,
formatted in braces, for a component exported by a container root. A direct FMU
model has no container level, so its guid is
`uuid5(NAMESPACE_URL, "pyssp_sysml2/<definition>")` and its `modelName` is the
bare definition name. `ExportIdentity` derives both spellings from one rule.
The `pyssp_sysml2/` prefix is deliberate and frozen: the v0.3.0 generator
derived the same guid, so migrating a build does not change a single guid.
Changing the prefix or the component spelling is a breaking change for every
consumer that stored a guid.

## Clock

`generation_time` is injected on the Python API and on
`pyfmi model-description --generation-time`. `None` means the current UTC time.
A naive datetime is refused. The document is stamped
`YYYY-MM-DDTHH:MM:SSZ`; two runs with the same injected time are byte-identical.

## Archive

`package_fmu` stages the tree and calls `pyssp_standard`'s `package_archive`,
which sorts entries, stamps every entry with the FMI epoch (2000-01-01), and
normalizes modes: metadata files `0o644`, files under `binaries/` `0o755`. A
repack from a fresh stage is byte-identical, and filesystem mtimes do not leak
into the bytes.

Ordering is also fixed outside the archive: components are exported sorted by
name, ports and fields follow declaration order, and Modelica package files are
returned sorted.
