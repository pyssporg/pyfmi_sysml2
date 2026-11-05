# Case: sensor

A storage-tank component with two scalar parameters, one scalar input, and one
output payload carrying a Boolean alongside two Reals.

## Artifacts

- `sensor.sysml`

**Conversion**: SysML v2 architecture -> the four FMI 2.0 artifacts
(`modelDescription.xml`, C headers, Modelica package, packaged `.fmu`)
**Requirement / fault**: a Boolean field must keep its type through the C
spelling and the FMI `Boolean` data type, and two authored parameter defaults
must survive as text; a Boolean degraded to `Real` or a lost `0.08` is a fault
**Level**: unit; the fixture is parsed input, not a generated artifact
**Input**: ported from
`/home/eriro/pwa/2_work/ssp_airplane/architecture/part_definition.sysml:143-155`
(`part def FuelSystem`) and its payloads in
`.../port_definitions.sysml:86-96`
**Expected**: package `Sensor`, part `Tank`, composition `SensorComposition`;
six scalar variables in value-reference order `0..5` — parameters
`parameters.capacity` (`3160.0`), `parameters.reserve` (`0.08`), input
`supply.rate`, and output fields `level.remaining`, `level.fraction`,
`level.empty`; every `level.*` variable is an output and therefore not writable
**Independent oracle**: `pycps_sysml2.load` parses the file, the FMI2 XSD and
semantic validator check the document, and the C headers are compiled by
`gcc -std=c11` and `g++ -std=c++17`
**Comparison**: byte-for-byte against the goldens under
`tests/golden/<subject>/sensor/`
**Normalization**: none
**Volatile fields**: none
**Update policy**: change the fixture and every affected golden in one commit;
regenerate with `UPDATE_GOLDENS=1`, never under `CI`
**Notes**: the only fixture whose output payload mixes `Real` and `Boolean`;
`empty` is what pins the `SENSOR_DATA_BOOLEAN` mapping tag
**Provenance**: ported from `ssp_airplane` and renamed. `FuelSystem` -> `Tank`,
`fuel_capacity_kg` -> `capacity` (`3160` -> `3160.0`), `reserve_fraction` ->
`reserve`, and both attributes moved from the part onto a `TankParameters`
parameter interface; `FuelConsumptionRate` -> `Rate`, `FuelLevelState` ->
`LevelState` with `fuel_remaining_kg`/`fuel_level_norm`/`fuel_starved` ->
`remaining`/`fraction`/`empty`; ports `fuel_consumption_rate` -> `supply` and
`fuelState` -> `level`; all `doc` comments dropped; `SensorComposition` added to
give the part a composition root

## What this case proves

That non-`Real` primitives keep their identity end to end, and that two authored
defaults reach the C instance struct and the FMI start attribute unchanged. No
other fixture has a mixed-type output payload.

## Update history

- 2026-11-05 — Fixture and record created, U3.7.
