# Fixtures

The architecture inputs every artifact golden is generated from. A fixture is
part of the contract: it is the only input a golden has, so it is reviewed like
the goldens are.

## Layout

```
tests/fixtures/<subject>/<subject>.sysml   the architecture
tests/fixtures/<subject>/case.md           its record
```

One `.sysml` file per directory, named after the directory, so
`conftest.fixture_path(subject, f"{subject}.sysml")` always resolves. Goldens
mirror the names: `tests/golden/<artifact>/<subject>/`.

A fixture that needs more than one load root puts the included package in a
subdirectory that follows the same rule (`packages/support/support.sysml`):
`packages.sysml` stays the primary root the convention points at, and the
included root is one more directory passed to `pycps_sysml2.load`.

| Subject | Purpose | Variables |
| --- | --- | --- |
| `minimal` | the floor: 1 parameter, 1 input, 1 output, one shared payload | 3 |
| `sensor` | a `Boolean` in an output payload and two authored defaults | 6 |
| `controller` | a `Real[2]` list parameter and a `String` parameter | 9 |
| `bus` | no parameters, seven ports, an `inout` port, reused payloads | 20 |
| `generator` | a direct `:> FmuModel` definition with no container root | 3 |
| `packages` | a two-root load: an included part definition with parts, and one bare name in both packages | 3 |

## Naming rule

The directory, the file, and the package name agree: `tests/fixtures/bus/`
contains `bus.sysml`, whose package is `Bus`. Every identifier is either an
architectural role (`in`, `out`, `shared`, `parameters`, `status`) or a neutral
term (`Signal`, `Rate`, `Command`, `Orientation`). Names from the architecture
this repository was ported from — aircraft, fuel, mission-computer vocabulary —
must not appear in a fixture; the generators must never depend on them.

## Inline documentation limit

A fixture may carry at most **15 lines** of inline documentation, meaning every
line of every `doc /* ... */` block counted together. Documentation is not
compiled, is not compared, and only widens the diff of a fixture change; the
prose belongs in `case.md`. The ported fixtures carry none.

## Provenance

A fixture record names where the fixture came from: either
`synthetic, authored for this repository` or the source file, line range, and
every rename, plus an explicit note for anything added that the source does not
have. A fixture whose record cannot state its provenance does not belong here.
`tests/test_fixture_policy.py` enforces the record, the naming, and the limit.
