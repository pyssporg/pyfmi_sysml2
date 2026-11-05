"""FMI 2.0 standard headers shipped with the package.

The three public FMI C headers are package data so an FMU build can take them
from ``pyfmi_sysml2`` instead of copying them into a fixture by hand. They are
the unmodified FMI 2.0.5 headers that ``pyssp_standard`` vendors; this package
owns delivering them to its consumers.
"""

from __future__ import annotations

from importlib import resources
from pathlib import Path

_PACKAGE = "pyfmi_sysml2"
_DIRECTORY = "fmi2_headers"


def fmi2_headers() -> tuple[Path, ...]:
    """Return the bundled FMI 2.0 standard headers as file paths.

    The headers are package data. An unpacked install (editable checkout or
    wheel) yields real ``Path`` objects; a zipped install cannot expose real
    paths and is refused rather than handing a non-path to a compiler.

    Returns:
        The sorted ``fmi2FunctionTypes.h``, ``fmi2Functions.h``, and
        ``fmi2TypesPlatform.h`` paths.

    Raises:
        RuntimeError: The package is not installed as an unpacked directory.
        FileNotFoundError: No headers are present in the bundled directory.
    """
    root = resources.files(_PACKAGE).joinpath(_DIRECTORY)
    if not isinstance(root, Path):
        raise RuntimeError(
            "pyfmi_sysml2 must be installed as an unpacked directory so the "
            "bundled FMI 2.0 headers have real file paths"
        )
    headers = tuple(sorted(root.glob("*.h")))
    if not headers:
        raise FileNotFoundError(
            f"no FMI 2.0 headers found in {root}; reinstall pyfmi_sysml2"
        )
    return headers
