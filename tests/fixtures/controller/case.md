# Case: controller

A three-field command input, two mixed-type outputs, and the only parameter
interface in the fixture set with a fixed-size array and a String.

## Artifacts

- `controller.sysml`

**Conversion**: SysML v2 architecture -> the four FMI 2.0 artifacts
(`modelDescription.xml`, C headers, Modelica package, packaged `.fmu`)
**Requirement / fault**: a `Real[2]` list parameter expands element-wise and a
`String` parameter has no FMI 2.0 scalar carrier, so the expansion and the
`STRING` mapping must both be exact; a single lost array element or a String
serialized as `Real` is a fault
**Level**: unit; the fixture is parsed input, not a generated artifact
**Input**: ported from
`/home/eriro/pwa/2_work/ssp_airplane/architecture/part_definition.sysml:119-141`
(`part def MissionComputer`) and the payloads in
`.../port_definitions.sysml:7-33,72-78`
**Expected**: package `Controller`, part `Controller`, composition
`ControllerComposition`; nine scalar variables in value-reference order `0..8` —
parameters `parameters.gains[0]` (`1.0`), `parameters.gains[1]` (`2.5`),
`parameters.label` (`"nominal"`), input fields `command.manual`, `command.auto`,
`command.mode`, and output fields `throttle.demand`, `throttle.enabled`,
`status.code`
**Independent oracle**: `pycps_sysml2.load` parses the file, the FMI2 XSD and
semantic validator check the document, and the C headers are compiled by
`gcc -std=c11` and `g++ -std=c++17` — the second compile is what proves `auto`
was escaped rather than emitted raw
**Comparison**: byte-for-byte against the goldens under
`tests/golden/<subject>/controller/`
**Normalization**: none; the array is expanded in declaration order and the
String default is emitted as authored
**Volatile fields**: none
**Update policy**: change the fixture and every affected golden in one commit;
regenerate with `UPDATE_GOLDENS=1`, never under `CI`
**Notes**: `auto` is a C and C++ keyword, so the field exercises the identifier
sanitizer in both the member name and the C array member spelling
**Provenance**: ported from `ssp_airplane` and renamed. `MissionComputer` ->
`Controller`, `manualInput`/`autopilotInput`/`fuelStatus` -> one `command` input,
`engineThrottle` -> `throttle`, `direction_command` -> `status`; the source
payloads (`PilotCommand`, `ThrottleCommand`) were re-authored at reduced width
as `Command {manual, auto, mode}` and `Throttle {demand, enabled}`, and a new
`Status {code}` payload carries the second output. All `doc` comments dropped;
`ControllerComposition` added. The `ControllerParameters` interface is a
coverage extension: `gains : Real[2]` and `label : String` do not exist in the
source draft, which declares no parameter interface at all — they are here only
because no ported source exercised a list or a String parameter

## What this case proves

That the two parameter kinds with no direct FMI 2.0 scalar analogue — a
fixed-length array and a String — reach every artifact with a defined shape, and
that a field named after a C keyword still yields headers both compilers accept.

## Update history

- 2026-11-05 — Fixture and record created, U3.7.
