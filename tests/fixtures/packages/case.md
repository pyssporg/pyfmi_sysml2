# Case: packages

A two-root load: the primary package declares the composition root and an
included package supplies a part definition with parts that the root uses. Both
packages declare a definition with the same bare name.

## Artifacts

- `packages.sysml` — the primary root, package `Packages`
- `support/support.sysml` — the included root, package `Support`

**Conversion**: SysML v2 architecture loaded from two roots -> the FMI 2.0
artifacts (`modelDescription.xml`, C headers, Modelica package, packaged `.fmu`)
**Requirement / fault**: a definition of the primary package is stored under its
bare name and a definition of any other package under `"<package>::<name>"`.
Root selection must compare stored keys on both sides; comparing a bare
`Definition.name` against a stored key counts the included `Unit`, which has
parts, as a second composition root and refuses the load as ambiguous
**Level**: component; the fixture is parsed input and the generated
modelDescription and C headers are the unit under test
**Input**: authored here, no external source
**Expected**: stored part keys `Leaf`, `PackagesComposition`, `Support::Leaf`,
`Support::Unit`; `resolve_system` returns `PackagesComposition`; one exported
component, `Leaf` — the included one, with parameter `bias` (default `0.5`) and
variables `bias`, `u.value`, `y.value`; `modelName` is
`PackagesComposition.Leaf`, `modelIdentifier` is `Leaf`, and every path and file
name is bare: the modelDescription lands in `Leaf/` and the headers are
`Packages_InterfaceCommon.h` and `Packages_Leaf.h`
**Independent oracle**: `pycps_sysml2.load` parses both roots and the FMI 2
validator checks the generated document; the expected names come from the
naming rule in `pyfmi_sysml2.interface`, not from a stored file
**Comparison**: `tests/test_package_roots.py` asserts the selected root, the
exported component, the artifact paths, and that no `::` appears in any name or
path; this subject has no golden, because its point is key selection rather than
bytes
**Normalization**: none; the injected clock is fixed by `conftest.GENERATION_TIME`
**Volatile fields**: none
**Update policy**: change the fixture and `tests/test_package_roots.py` in one
commit; there is no golden to regenerate
**Notes**: the only fixture whose include root is a subdirectory, so the
directory and its file still share a name; `Leaf` is declared in both packages
on purpose, and the root reaches the included one with a qualified type name
(`part unit : Support::Unit`)
**Provenance**: synthetic, authored for this repository; no external source and
no licence obligation

## What this case proves

That a package-scoped namespace does not turn an included part definition into a
second composition root, and that the qualifier stays in the namespace: no
`::` reaches a model name, a model identifier, a header stem, or an output path.

## Update history

- 2026-11-05 — Fixture and record created for the stored-key root rule.
