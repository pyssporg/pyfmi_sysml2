# Case: cross-artifact/consistency

## Artifacts

- `<Component>/modelDescription.xml`
- `<Package>_InterfaceCommon.h` and `<Package>_<Component>.h`
- `<Component>.fmu` (with `modelDescription.xml`, `binaries/linux64/<Component>.so`, and `sources/<Package>_<Component>.h`)

No golden artifact is stored under this directory: the three artifacts are
compared with each other, not with a recorded file.

**Conversion**: SysML v2 architecture -> {modelDescription, C headers, FMU}
**Requirement / fault**: U3.6; three generators that each read the shared
`interface` reduction must still agree on the variable set, the causalities, and
the component identity after they have been written to disk
**Level**: contract
**Input**: `tests/fixtures/{minimal,sensor,controller,bus}/<subject>.sysml`,
with `generation_time=datetime(2026, 1, 1, tzinfo=timezone.utc)`
**Expected**: `check_artifacts` accepts all four fixtures; the modelDescription
and the component header carry the same value references and variable names in
the same order; every `causality="output"` variable appears in
`ModelStructure/Outputs` and `InitialUnknowns` at its 1-based position and no
other variable does; `modelIdentifier` equals the binary stem and the component
name; the archived header is byte-identical to the header on disk
**Independent oracle**: `pyssp_standard.standard.fmi2.codec.Fmi2ModelDescriptionXmlCodec`
and `xml.etree.ElementTree` for the XML, regular expressions over the enum and
`initialize_vr_map` text for the header, `zipfile` for the archive, and
`gcc -std=c11 -fsyntax-only` / `g++ -std=c++17 -fsyntax-only` for the headers
**Comparison**: identity across artifacts, plus five mutation tests that must
make the gate raise (`VR set mismatch` for a dropped ScalarVariable and for a
dropped header enumerator, `modelIdentifier` for a renamed identifier and for a
renamed binary, `ModelStructure mismatch` for a flipped output causality)
**Normalization**: none; the clock is injected, so every field is deterministic
**Volatile fields**: none
**Update policy**: no golden to refresh. When a generator changes, re-run
`./venv/bin/python -m pytest tests/test_cross_artifact.py -q` and extend the
mutation list if the gate gains a check without a mutation
**Notes**: the gate reads artifacts only through parsers that share no code with
the generators (`_sanitize` is re-implemented in the test on purpose). It cannot
check that the binary is loadable, that the header's struct layout matches the C
ABI of the real model, or that start values in the header equal `start` in the
XML beyond the primitive type tag and the writability flag

## What this case proves

That the modelDescription, the C header, and the packaged FMU describe one
component: the same value references, the same variable order, a consistent
ModelStructure, and one agreed identity. The mutation tests prove the gate
fails when any single artifact drifts, so a green run is evidence rather than a
tautology.

## Update history

- 2026-11-05 — Initial case, U3.6.
