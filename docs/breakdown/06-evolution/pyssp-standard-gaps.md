---
id: INFO-014
type: info
title: pyssp_standard gaps blocking v0.2.0
summary: Two upstream gaps remain: the FMU facade cannot carry sources/, and SourceFiles/annotation content is not modelled.
date: 2026-11-05
status: current
---

# pyssp_standard gaps blocking v0.2.0

Two limitations in the pinned `experimental-pyssp-standard` build shape what
this library can emit. Neither is worked around by hand-writing XML.

## Sources and the FMU facade

`FMU.create` cannot carry a `sources/` group. The packager therefore stages the
tree itself and calls `package_archive`, which does include `sources/`. The
workaround is deliberate and tested; a facade that accepts sources would let the
packager drop one layer.

## SourceFiles and annotations

The FMI 2.0 model allows `SourceFiles` (`fileName`, `language`, and related
attributes) and vendor annotations. The pinned document model exposes neither,
so the generated modelDescription carries no `SourceFiles` entry and no
`VendorAnnotations`. That is acceptable for v0.1.0 because the binary is built
outside this library, but it blocks two v0.2.0 goals:

- declaring the C source and its language alongside the binary;
- carrying author, version, and license annotations that a consumer may read.

The fix belongs upstream: extend the model objects and the codec, then consume
them here. Until then neither element is emitted, and adding one by hand-written
XML is not an acceptable workaround.

## Verification

Re-check both gaps after any `pyssp_standard` version bump; the pinned URL is
v0.9.2.dev0. If the facade gains `sources/`, delete the staging path and its
tests in the same change.
