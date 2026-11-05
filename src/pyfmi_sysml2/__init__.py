"""Generate FMI 2.0 CoSimulation artifacts from a SysML v2 architecture.

The SysML dialect is owned by :mod:`pycps_sysml2`; this package implements the
FMI half of it. The public surface is one function per artifact plus the
``pyfmi`` command line:

- :func:`generate_model_description` — ``modelDescription.xml``
- :func:`generate_c_headers` — C interface headers
- :func:`generate_modelica` — Modelica connectors and package files
- :func:`package_fmu` — the packaged ``.fmu``
"""

from pyfmi_sysml2.interface import Component, Variable, components

__version__ = "0.1.0"

__all__ = [
    "Component",
    "Variable",
    "__version__",
    "components",
]
