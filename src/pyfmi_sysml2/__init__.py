"""Generate FMI 2.0 CoSimulation artifacts from a SysML v2 architecture.

The SysML dialect is owned by :mod:`pycps_sysml2`; this package implements the
FMI half of it. The public surface is one function per artifact plus the
``pyfmi`` command line:

- :func:`generate_model_description` — ``modelDescription.xml``
- :func:`generate_c_headers` — C interface headers
- :func:`generate_modelica` — Modelica connectors and package files
- :func:`package_fmu` — the packaged ``.fmu``
- :func:`fmi2_headers` — the bundled FMI 2.0 standard C headers
"""

from pyfmi_sysml2.c_interface import generate_c_headers
from pyfmi_sysml2.headers import fmi2_headers
from pyfmi_sysml2.interface import Component, Variable, components
from pyfmi_sysml2.model_description import generate_model_description
from pyfmi_sysml2.modelica import generate_modelica
from pyfmi_sysml2.package import package_fmu, stage_fmu

__version__ = "0.2.0"

__all__ = [
    "Component",
    "Variable",
    "__version__",
    "components",
    "fmi2_headers",
    "generate_c_headers",
    "generate_model_description",
    "generate_modelica",
    "package_fmu",
    "stage_fmu",
]
