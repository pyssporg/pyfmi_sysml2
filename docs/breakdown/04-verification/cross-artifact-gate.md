---
id: TEST-002
type: test
title: Cross-artifact consistency gate
summary: check_artifacts() reads modelDescription, the C header, and the packed FMU with independent parsers and proves they describe one component; mutation tests prove it fails when one is broken.
date: 2026-11-05
status: current
---

# Cross-artifact consistency gate

`tests/test_cross_artifact.py` writes the three artifacts for each fixture, then
reads them back with parsers that do not share code with the writers: the FMI
codec and `ElementTree` for XML, regular expressions for the header, `zipfile`
for the archive. `check_artifacts()` asserts three equalities:

- **VR set** — every `valueReference` in `modelDescription.xml` appears in the
  component header's VR enum, and the enum has no extra entry; the identifiers
  are re-derived by the gate, not imported from the generator.
- **Identifier** — the `modelIdentifier` equals the stem of the binary stored
  under `binaries/<platform>/`, and the header's prefix names the same package.
- **Causality** — every `causality="output"` variable is in
  `ModelStructure/Outputs` and `InitialUnknowns`, index-ordered, and the C
  mapping marks exactly those variables non-writable.

The gate has teeth by mutation. Each of these must raise `ArtifactMismatch`:

- dropping a ScalarVariable from the XML;
- dropping an enumerator from the header;
- renaming `modelIdentifier`;
- renaming the packaged binary;
- flipping an output's causality to input.

The fixtures are generated into a temporary directory, so the gate proves the
current code; the goldens prove the bytes have not moved.
