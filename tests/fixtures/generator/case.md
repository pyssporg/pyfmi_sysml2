# Case: generator

The direct export pattern: the part definition that carries the FMI interface is
itself the FMU model (`:> FmuModel`), and there is no container composition
above it.

## Artifacts

- `generator.sysml`

**Conversion**: SysML v2 architecture -> the four FMI 2.0 artifacts
(`modelDescription.xml`, C headers, Modelica package, packaged `.fmu`)
**Requirement / fault**: the marked definition is the export unit itself, so
`modelName`, `modelIdentifier`, and the guid must use the bare definition name
(`Generator`, not `Generator.Generator`) and the header must not repeat the
package name (`Generator.h`, not `Generator_Generator.h`); any doubled identity
is a fault
**Level**: unit; the fixture is parsed input, not a generated artifact
**Input**: synthetic, authored for this repository; it mirrors the direct-FMU
shape the `FmuModel` role marker exists for, with neutral names only
**Expected**: package `Generator`, one exported component `Generator`, three
scalar variables in value-reference order `0..2` — parameters `parameters.gain`
(`2.0`) and `parameters.offset` (`0.5`), then output `y.value`; modelDescription
`modelName` and `modelIdentifier` both `Generator`; guid
`uuid5(NAMESPACE_URL, "pyssp_sysml2/Generator")`; C header files
`Generator_InterfaceCommon.h` and `Generator.h`
**Independent oracle**: `pycps_sysml2.load` parses the file, the FMI2 XSD and
semantic validator check the document, and the C headers are compiled by
`gcc -std=c11` and `g++ -std=c++17`
**Comparison**: byte-for-byte against the goldens under
`tests/golden/<subject>/generator/`
**Normalization**: none; parameters precede ports and the single output field
keeps its declared name
**Volatile fields**: none
**Update policy**: change the fixture and every affected golden in one commit;
regenerate with `UPDATE_GOLDENS=1`, never under `CI`
**Notes**: the fixture is a standalone architecture root, so it declares the
role and metadata markers other fixtures also declare locally
(`FmuModel`, `FmuMetadata`, `ParameterInterface`, `ParameterSet`); the marker
names are the dialect vocabulary, not a second definition of them. The
`fmu_meta` attribute is authoring data and is not part of the FMI variable set.
**Provenance**: synthetic, authored for this repository. The name `Generator`
and the gain/offset parameter shape are the generic direct-FMU example; no
architecture-specific vocabulary from a ported source is used.

## What this case proves

That a marked part definition is selected as the export unit without a container
root, and that its single component keeps one identity across the model
description, the C header names, and the packaged archive.

## Update history

- 2026-11-05 — Fixture and record created for the direct `FmuModel` export
  pattern.
