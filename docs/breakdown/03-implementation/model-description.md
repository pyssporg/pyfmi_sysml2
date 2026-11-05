---
id: INFO-005
type: info
title: modelDescription generation
summary: model_description.py assembles a pyssp_standard FMI 2 document from the reduction, stamps the clock, serializes, validates, then writes one file per component.
date: 2026-11-05
status: current
---

# modelDescription generation

`model_description_document()` builds an `Fmi2ModelDescriptionDocument`; nothing
in this module writes XML by hand.

Document fields:

- `fmi_version="2.0"`, `model_name="<composition>.<component>"`;
- `guid` from the frozen uuid5 namespace, `generation_tool="pyfmi_sysml2 tooling"`;
- `generation_date_and_time` from the injected clock;
- `variable_naming_convention="structured"`;
- `interface_type="CoSimulation"` and `capabilities` with
  `model_identifier=<component>` — both are required for the codec to emit the
  interface element;
- one `Fmi2ScalarVariable` per reduction variable, `start` already rendered as
  FMI text;
- `ModelStructure` outputs and initial unknowns from `component.outputs`, using
  the 1-based `Variable.index`;
- `DefaultExperiment` only when the composition carries the start/stop control
  attributes.

`render_model_description()` serializes with
`Fmi2ModelDescriptionXmlCodec` and validates the object and text with
`Fmi2ModelDescriptionValidator` before returning. `generate_model_description()`
writes `<output>/<Component>/modelDescription.xml` per selected component and
returns the paths; a named component that is not exported is a `ValueError`.

The `start` text is produced by `pycps_sysml2.core.format_value`, so a Boolean
is `true`/`false`, never `str(True)`.

Parity with `pyssp_sysml2` v0.3.0 was checked against the frozen generator on
its `identity` golden: `modelName`, `guid`, every `ScalarVariable`, and both
`ModelStructure` groups are identical. Three deliberate deviations remain:
`generationTool` names this library, and the empty `description=""`,
`version="1.0"`, and `numberOfEventIndicators="0"` root attributes are not
invented (FMI authoring attributes are a v0.2.0 item).
