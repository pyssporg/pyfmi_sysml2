# Case: bus

The widest component: no parameters, seven ports, four payload definitions
reused across directions, and the only `inout` port in the fixture set.

## Artifacts

- `bus.sysml`

**Conversion**: SysML v2 architecture -> the four FMI 2.0 artifacts
(`modelDescription.xml`, C headers, Modelica package, packaged `.fmu`)
**Requirement / fault**: FMI 2.0 has no bidirectional scalar variable, so an
`inout` port must degrade to an input rather than disappear; four payloads used
by seven ports must be emitted once each, and a component with no parameter
interface must emit no `parameter`/`fixed` variables
**Level**: unit; the fixture is parsed input, not a generated artifact
**Input**: ported from
`/home/eriro/pwa/2_work/ssp_airplane/architecture/part_definition.sysml:180-196`
(`part def Environment`) and the payloads in
`.../port_definitions.sysml:42-105`
**Expected**: package `Bus`, part `Bus`, composition `BusComposition`; twenty
scalar variables in value-reference order `0..19` — `actuation.*` (3),
`orientation_in.*` (3), `position_in.*` (3), `shared.*` (3), `orientation_out.*`
(3), `position_out.*` (3), `status.*` (2); every `shared.*` entry is an input and
writable, every `*_out.*` and `status.*` entry is an output and read-only
**Independent oracle**: `pycps_sysml2.load` parses the file, the FMI2 XSD and
semantic validator check the document, the C headers are compiled by
`gcc -std=c11` and `g++ -std=c++17`, and the enum order is cross-checked against
`Component.variables`
**Comparison**: byte-for-byte against the goldens under
`tests/golden/<subject>/bus/`
**Normalization**: none; payload structs appear in first-use order, which the
sorted component list and each component's declaration order fix
**Volatile fields**: none
**Update policy**: change the fixture and every affected golden in one commit;
regenerate with `UPDATE_GOLDENS=1`, never under `CI`
**Notes**: only `inout` is covered, not a direction-less port: the fixture
authors `inout port shared : Orientation` and no bare `port`, and the source has
neither. A bare port and an `inout` port both reduce to `direction=None`, so one
of the two spellings is enough to reach that branch; adding a bare port would
duplicate the same code path
**Provenance**: ported from `ssp_airplane` and renamed. `Environment` -> `Bus`,
`actuation_command` -> `actuation`, `direction_command` -> `orientation_in`,
`lift` -> `position_in`, `orientation` -> `orientation_out`, `location` ->
`position_out`, `flight_status` -> `status`; `SurfaceActuationCommand`,
`OrientationEuler`, `PositionXYZ` and `FlightStatusPacket` were re-authored at
reduced width as `Actuation`, `Orientation`, `Position` and `StatusPacket`, and
the source input `thrust_in` was dropped. `inout port shared : Orientation` is
an addition — the source has no `inout` and no undirected port. All `doc`
comments dropped; `BusComposition` added

## What this case proves

That the widest reduction in the fixture set keeps every field exactly once and
in declaration order, that payload reuse does not duplicate a C struct, and that
a direction FMI cannot express degrades to an input instead of being dropped.

## Update history

- 2026-11-05 — Fixture and record created, U3.7.
