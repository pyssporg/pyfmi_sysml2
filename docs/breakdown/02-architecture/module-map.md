---
id: INFO-002
type: info
title: Module map
summary: Seven modules behind one facade; dependency flows sysmlpy to pycps_sysml2 to pyfmi_sysml2 to pyssp_standard.fmi2, never through pyssp_sysml2.
date: 2026-11-05
status: current
---

# Module map

`src/pyfmi_sysml2/` is split by artifact. `__init__.py` is the canonical public
surface and re-exports only the generator functions and the reduction types.

```
src/pyfmi_sysml2/
├── __init__.py           # public surface: four generators, stage_fmu, types
├── cli.py                # `pyfmi` entry point, one subcommand per artifact
├── interface.py          # the variable reduction: the single source of truth
├── model_description.py  # modelDescription.xml document and serializer
├── c_interface.py        # common and per-component C headers
├── headers.py            # bundled FMI 2.0 standard headers
├── modelica.py           # Modelica package and connectors
└── package.py            # FMU staging and deterministic archive
```

Dependency direction, one way only:

```
sysmlpy -> pycps_sysml2 -> pyfmi_sysml2 -> pyssp_standard (fmi2, archive)
```

- `pycps_sysml2` owns parsing, the IR, parameters, ports, and controls.
- `pyssp_standard` owns FMI 2.0 documents, the codec, the validator, and the
  archive writer.
- `pyssp_sysml2` is not a dependency and must never be imported; the two
  artifact libraries are siblings, not layers.

Every generator imports `pyfmi_sysml2.interface`; none of them re-derives the
variable set. `cli.py` imports the generators only, so the shell surface cannot
drift from the Python surface.
