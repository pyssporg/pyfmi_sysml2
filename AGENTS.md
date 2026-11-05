# AGENTS

## Vision first (required)

Before you read code, edit files, or plan a change, read the project vision:

**`docs/breakdown/00-intent/intent.md`**

It states why this repository exists, what it commits to, and what it refuses to
become. It is the first document to read, not a reference of last resort.

- Read it in full before making any change to code, tests, docs, or artifacts.
- Judge every proposed change against it. If a change conflicts with the vision,
  its commitments, goals, or non-goals, stop and surface the conflict; do not
  implement it silently.
- If the work shows the long-term direction is wrong, change the vision
  deliberately first, then the code. Never let the repository drift away from
  its stated intent.

## Rules

1. **Don't assume. Surface tradeoffs.** If a contract is ambiguous, stop and say
   so rather than picking a behaviour silently.
2. **Minimum code that solves the problem.** Nothing speculative.
3. **Touch only what you must.** Clean up only your own mess.
4. **Define success criteria and verify.**

## Repository Focus

`pyfmi_sysml2` generates FMI 2.0 CoSimulation artifacts from a SysML v2
architecture: `modelDescription.xml`, C interface headers, Modelica connectors,
and a packaged `.fmu`. The artifact is the library boundary; the `pyfmi` CLI and
the four generator functions are the public surface.

- The SysML dialect is owned by `pycps_sysml2`; this package implements the FMI
  half of that contract.
- FMI XML is owned by `pyssp_standard.standard.fmi2`; this package maps the
  reduction onto it.
- Current state, contracts, and design rationale live in `docs/breakdown/`; the
  code is the source of truth when the two disagree.

## Hard constraints

- **Never import `pyssp_sysml2`.** The two artifact libraries are siblings.
  Dialect access goes through `pycps_sysml2`; SSP emission is not this
  repository's job.
- **Never hand-roll ElementTree for FMI XML.** Build, serialize, and validate
  through `pyssp_standard.standard.fmi2` (`Fmi2ModelDescriptionDocument`,
  `Fmi2ModelDescriptionXmlCodec`, `Fmi2ModelDescriptionValidator`).
- **Every artifact is reproducible from an injected `generation_time`.** The
  clock is a parameter, not an ambient read; a naive datetime is refused. The
  same architecture and clock produce byte-identical files, including the
  archive.
- **The built artifact is the unit under test.** Assertions run against the
  generated file or the packed `.fmu`, not against an intermediate string that
  the writer might not use.
- **One variable set.** Every generator reads `pyfmi_sysml2.interface`; none
  re-derives variables, causalities, or value references.
- **`linux64` only.** Do not widen the platform allow-list without a decision.

## Code guidelines

- Keep changes direct and explicit. Minimize duplication, but do not hide the
  document assembly behind abstractions.
- Prefer small modules with one artifact each; a generator returns the paths it
  wrote.
- Treat this as experimental software: interfaces need not be stable, and
  clarity outranks compatibility shims.
- Avoid thin wrappers unless they buy something substantial. A wrapper that only
  renames a library call is noise.
- Preserve user changes in a dirty worktree; never revert unrelated edits.

## Conventions

- `README.md` is the landing page for users; `AGENTS.md` is for contributors.
- Current state lives in `docs/breakdown/` leaves, in the present tense. Dated
  decisions live in `docs/archive/archive.zip`, read with `pb archive`; never
  add per-layer `decisions/` folders.
- Regenerate `docs/archive/README.md`, `design-choice-log.md`, and
  `traceability-map.md` with `pb registers`; never edit them by hand.
- Every fixture carries a `case.md` with the artifact, oracle, comparison, and
  update policy. Goldens are compared byte-for-byte; `UPDATE_GOLDENS=1`
  rewrites them locally and is ignored under `CI`.
- Keep docs aligned with the actual CLI, file layout, and dependency pins.

## Environment

- Python >= 3.10; the repository ships `./venv`.
- Install: `./venv/bin/pip install -e ".[dev]"`. Both runtime dependencies are
  direct-URL wheels pinned to sibling GitHub releases.
- Tests: `./venv/bin/python -m pytest -q`; the CI subset is
  `./venv/bin/python -m pytest -m "not slow"`.
- Lint: `./venv/bin/ruff check src tests`.
- Oracles: `gcc`/`g++` syntax-check the headers and `omc` checks the Modelica
  package; both skip with a reason when absent.
- Breakdown checks:
  `python3 <pb> check --strict --root docs/breakdown` and
  `python3 <pb> node-size --strict --root docs/breakdown`, where `<pb>` is the
  product-breakdown skill's `scripts/pb`.
