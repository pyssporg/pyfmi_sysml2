---
id: CP-001
type: capability
title: FMI 2.0 CoSimulation artifact contract
summary: A generated FMU is a deterministic zip with a validated modelDescription at the root and an executable binary named by modelIdentifier.
date: 2026-11-05
status: current
---

# FMI 2.0 CoSimulation artifact contract

A generated artifact is valid when all of the following hold.

Archive layout:

- `modelDescription.xml` at the zip root, never nested;
- `binaries/linux64/<modelIdentifier>.so`, executable;
- `sources/` for generated headers, when supplied;
- `resources/` and `documentation/` only when supplied.

`modelDescription.xml`:

- `fmiVersion="2.0"`, a `modelName`, and a `guid` are present;
- exactly one `CoSimulation` element, carrying `modelIdentifier`;
- every `ScalarVariable` has a unique `name` and a unique `valueReference`
  and exactly one typed child;
- `ModelStructure/Outputs` holds exactly the `causality="output"` variables,
  index-ordered; `InitialUnknowns` is index-ordered without duplicates;
- the document passes `Fmi2ModelDescriptionValidator` (semantic and XSD).

Consistency:

- the VR set is identical across modelDescription, C header, and packager;
- the binary stem equals the interface `modelIdentifier`;
- repacking twice from equal inputs yields identical bytes;
- `generationDateAndTime` comes from the injected time, not the wall clock.

The schema allows more than this contract emits. Optional FMI features that the
dialect does not author are absent rather than invented.
