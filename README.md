# pyfmi_sysml2

Generate FMI 2.0 CoSimulation artifacts from a SysML v2 architecture:
`modelDescription.xml`, C interface headers, Modelica connectors, and a packaged
`.fmu`.

**Library boundary.** The SysML dialect is read *only* through
[`pycps_sysml2`](https://github.com/pyssporg/pycps_sysml2); FMI XML is built,
serialized, and validated *only* through `pyssp_standard.standard.fmi2`. This
package must never depend on `pyssp_sysml2`: the two artifact libraries are
siblings, not layers. What crosses to another project is the artifact — FMI XML,
C headers, Modelica text, or the `.fmu` archive.

- Users: this file and `pyfmi --help`.
- Contributors: `AGENTS.md`, then `docs/breakdown/00-intent/intent.md`.
- Current contracts and design: `docs/breakdown/README.md`.

## Install

The two runtime dependencies are direct-URL wheels pinned to sibling GitHub
releases (`pycps-sysml2` v0.1.0 and `experimental-pyssp-standard` v0.9.2.dev0),
so the tags must exist before any install resolves.

From a checkout:

```bash
python3 -m venv venv
./venv/bin/pip install -e ".[dev]"
```

From a built wheel, `pip install pyfmi_sysml2-<version>-py3-none-any.whl`
resolves the same two URLs. Both dependencies are immutable release assets, not
index lookups.

## CLI

`pyfmi` has one subcommand per artifact. The three generators default to
`build/`; `pyfmi package` requires an output path. Every written path is printed
on stdout, one per line. Handled model or input errors print
`pyfmi: <message>` on stderr and exit 1; argument errors keep argparse's exit 2.

### `pyfmi --help`

```text
usage: pyfmi [-h] COMMAND ...

Generate FMI 2.0 CoSimulation artifacts from a SysML v2 architecture.

positional arguments:
  COMMAND
    model-description
                     Write modelDescription.xml per component.
    c-headers        Write C interface headers.
    modelica         Write a Modelica interface package.
    package          Write a deterministic .fmu archive.

options:
  -h, --help         show this help message and exit

The three generators write to build/ unless -o/--output is given; pyfmi
package requires an output archive path.
```

### `pyfmi model-description --help`

```text
usage: pyfmi model-description [-h] [-o OUT] [--composition NAME]
                               [--component NAME] [--generation-time ISO8601]
                               SOURCE

Write modelDescription.xml per component to an output directory.

positional arguments:
  SOURCE                A .sysml file or a directory containing them.

options:
  -h, --help            show this help message and exit
  -o OUT, --output OUT  Output directory (default: build).
  --composition NAME    Composition part definition to export (default: the
                        single root).
  --component NAME      Restrict the output to one exported component.
  --generation-time ISO8601
                        Fixed generationDateAndTime, for example
                        2026-01-01T00:00:00Z (default: now).
```

### `pyfmi c-headers --help`

```text
usage: pyfmi c-headers [-h] [-o OUT] [--composition NAME] [--prefix NAME]
                       SOURCE

Write the C interface headers to an output directory.

positional arguments:
  SOURCE                A .sysml file or a directory containing them.

options:
  -h, --help            show this help message and exit
  -o OUT, --output OUT  Output directory (default: build).
  --composition NAME    Composition part definition to export (default: the
                        single root).
  --prefix NAME         Header prefix and C type prefix (default: the package
                        name).
```

### `pyfmi modelica --help`

```text
usage: pyfmi modelica [-h] [-o OUT] [--composition NAME] [--package NAME]
                      [--within NAME]
                      SOURCE

Write the Modelica interface package to an output directory.

positional arguments:
  SOURCE                A .sysml file or a directory containing them.

options:
  -h, --help            show this help message and exit
  -o OUT, --output OUT  Output directory (default: build).
  --composition NAME    Composition part definition to export (default: the
                        single root).
  --package NAME        Root Modelica package name (default:
                        GeneratedInterfaces).
  --within NAME         Enclosing Modelica scope for the root package.
```

### `pyfmi package --help`

```text
usage: pyfmi package [-h] -o OUT --model-description PATH --binary PATH
                     [--platform NAME] [--header PATH] [--resource PATH]
                     [--documentation PATH]

Write a deterministic .fmu archive to the output path.

options:
  -h, --help            show this help message and exit
  -o OUT, --output OUT  Output .fmu archive path (required).
  --model-description PATH
                        FMI 2.0 modelDescription.xml for the archive root.
  --binary PATH         Built shared library; its stem must be the
                        modelIdentifier.
  --platform NAME       Platform directory under binaries/ (default: linux64).
  --header PATH         Generated header to include under sources/
                        (repeatable).
  --resource PATH       File or directory to include under resources/
                        (repeatable).
  --documentation PATH  File or directory to include under documentation/
                        (repeatable).
```

Example:

```bash
pyfmi model-description architecture/plant.sysml -o build \
  --generation-time 2026-01-01T00:00:00Z
pyfmi c-headers architecture/plant.sysml -o build
pyfmi modelica architecture/plant.sysml -o build
pyfmi package build/Plant.fmu \
  --model-description build/Tank/modelDescription.xml \
  --binary build/Tank.so \
  --header build/Plant_InterfaceCommon.h
```

## Python API

The package exports four generator functions, `fmi2_headers`, `stage_fmu`, and
the reduction types (`Component`, `Variable`, `components`).

```python
def generate_model_description(
    source: Path | str | Architecture,
    output_dir: Path | str,
    *,
    composition: str | None = None,
    component: str | None = None,
    generation_time: datetime | None = None,
) -> list[Path]: ...

def generate_c_headers(
    source: Architecture | str | PathLike[str],
    output_dir: str | PathLike[str],
    *,
    composition: str | None = None,
    prefix: str | None = None,
) -> list[Path]: ...

def generate_modelica(
    source: Architecture | str | Path,
    output_dir: str | Path,
    *,
    package: str = "GeneratedInterfaces",
    within: str | None = None,
    composition: str | None = None,
) -> list[Path]: ...

def fmi2_headers() -> tuple[Path, ...]: ...

def package_fmu(
    output: str | Path,
    *,
    model_description: str | Path,
    binary: str | Path,
    platform: str = "linux64",
    headers: tuple[str | Path, ...] | list[str | Path] = (),
    resources: tuple[str | Path, ...] | list[str | Path] = (),
    documentation: tuple[str | Path, ...] | list[str | Path] = (),
    stage_dir: str | Path | None = None,
) -> Path: ...
```

`source` is a `.sysml` file, a directory of them, or an already loaded
`pycps_sysml2.Architecture`. `generation_time=None` stamps the current UTC time;
pass a timezone-aware datetime for reproducible output. `fmi2_headers()` returns
the bundled FMI 2.0 standard headers as real file paths, so an FMU build can pass
them to `package_fmu` without copying them into the fixture. `package_fmu` stages
the tree itself because the `pyssp_standard` `FMU.create` facade cannot carry
`sources/`.

```python
from datetime import datetime, timezone
from pathlib import Path

import pyfmi_sysml2

source = Path("architecture/plant.sysml")
out = Path("build")
stamp = datetime(2026, 1, 1, tzinfo=timezone.utc)

pyfmi_sysml2.generate_model_description(source, out, generation_time=stamp)
pyfmi_sysml2.generate_c_headers(source, out)
pyfmi_sysml2.generate_modelica(source, out)

# The binary stem must equal the interface modelIdentifier (here: Tank).
pyfmi_sysml2.package_fmu(
    out / "Plant.fmu",
    model_description=out / "Tank/modelDescription.xml",
    binary=out / "Tank.so",
    headers=[out / "Plant_InterfaceCommon.h"],
)
```

## Generated artifact set

- `<out>/<Component>/modelDescription.xml` — one per exported component (a
  container root exports its leaves; a `:> FmuModel` definition exports itself).
- `<out>/<Prefix>_InterfaceCommon.h` — port payload structs, `DataType` enum,
  and `VrMapping`; plain C11.
- `<out>/<Prefix>_<Component>.h` — VR enum, `VrCount`, and the C++ `Instance`
  plus `initialize_vr_map()`; a direct FMU model whose definition names the
  package uses that name once (`Generator.h`).
- `<out>/<Package>/package.mo`, `package.order`, `Interfaces.mo`,
  `GeneratedInterfaces.mo` — one connector per port definition.
- `<archive>.fmu` — `modelDescription.xml` at the root,
  `binaries/linux64/<modelIdentifier>.so`, and `sources/`, `resources/`,
  `documentation/` when supplied.

`Prefix` defaults to the architecture package name; `Package` defaults to
`GeneratedInterfaces`. Value references restart at 0 per component: parameters
first, then ports in declaration order, then fields.

## Common errors

- **`generation_time must be timezone-aware`** — pass
  `datetime(..., tzinfo=timezone.utc)` or the CLI form
  `2026-01-01T00:00:00Z`. A naive time is refused so the artifact cannot depend
  on the host's locality.
- **Flat parameter attribute rejected** — parameters come from the parameter
  dialect (`in port parameters ...`), never from attributes on a part.
- **`platform 'windows64' is not supported; supported platforms: linux64`** —
  v0.1.0 emits `linux64` only; do not widen the allow-list ad hoc.
- **`modelIdentifier 'Tank' does not match binary stem 'libTank'`** — name the
  shared library exactly `<modelIdentifier>.so` (or pass the matching
  `--platform` binary).
- **`Cannot pick a composition root`** — several `:> FmuModel` definitions, or
  several part definitions that have parts and are unused; pass
  `--composition NAME`.
- **Multiplicity is not a fixed length** — FMI 2.0 needs one scalar per element;
  use a fixed list size.

## Development

```bash
./venv/bin/ruff check src tests
./venv/bin/python -m pytest -m "not slow"     # CI subset
./venv/bin/python -m pytest                   # includes the omc oracle
UPDATE_GOLDENS=1 ./venv/bin/python -m pytest  # rewrite goldens locally
```

Goldens are compared byte-for-byte and `UPDATE_GOLDENS` is ignored when `CI` is
set. The header tests use `gcc -std=c11 -fsyntax-only` and
`g++ -std=c++17 -fsyntax-only`; the Modelica test uses `omc loadFile` +
`checkModel` and skips when `omc` is absent. See
`docs/breakdown/04-verification/README.md`.

## Migrating from `pyssp_sysml2`

`pyssp_sysml2 generate fmi` was removed in `pyssp_sysml2` v0.4.0. Use `pyfmi`
instead:

| removed | replacement |
|---|---|
| `pyssp_sysml2 generate fmi --architecture ...` | `pyfmi model-description ...` |
| FMI C headers from the same generator | `pyfmi c-headers ...` |
| Modelica connector export | `pyfmi modelica ...` |
| FMU packaging | `pyfmi package ...` |

The artifacts are migration-compatible: a container root keeps the `guid`
namespace string `pyssp_sysml2/<composition>/<component>` and the
`<composition>.<component>` `modelName`. A direct `:> FmuModel` definition uses
`pyssp_sysml2/<definition>` and the bare `<definition>` name, so rebuilding with
`pyfmi` does not change identity.
