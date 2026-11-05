---
id: INFO-009
type: info
title: CLI
summary: The pyfmi entry point has four subcommands, prints one written path per line, exits 1 on handled model or input errors, and 2 on argument errors.
date: 2026-11-05
status: current
---

# CLI

`pyproject.toml` maps `pyfmi = "pyfmi_sysml2.cli:main"`. The four subcommands
mirror the four Python generators:

- `pyfmi model-description SOURCE [-o OUT] [--composition NAME]
  [--component NAME] [--generation-time ISO8601]`
- `pyfmi c-headers SOURCE [-o OUT] [--composition NAME] [--prefix NAME]`
- `pyfmi modelica SOURCE [-o OUT] [--composition NAME] [--package NAME]
  [--within NAME]`
- `pyfmi package -o OUT --model-description PATH --binary PATH
  [--platform NAME] [--header PATH] [--resource PATH] [--documentation PATH]`

Behaviour:

- `SOURCE` is a `.sysml` file or a directory of them, loaded by `pycps_sysml2`.
- The three generators default to `build/`; `package` requires an output path.
- `--header`, `--resource`, and `--documentation` are repeatable.
- Every written path is printed on stdout, one per line.
- `ValueError`, `KeyError`, and `FileNotFoundError` print `pyfmi: <message>` on
  stderr and return 1; argparse keeps exit 2; anything unexpected propagates.
- `--generation-time` accepts the emitted `...Z` form or an ISO 8601 form with
  an offset; a naive time is rejected.

The CLI adds no behaviour the API lacks: each handler calls one generator with
the parsed arguments.
