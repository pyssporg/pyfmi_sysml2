"""Contract: the package ships the public FMI 2.0 headers as real files."""

from __future__ import annotations

import pytest

import pyfmi_sysml2

pytestmark = pytest.mark.unit

EXPECTED = (
    "fmi2FunctionTypes.h",
    "fmi2Functions.h",
    "fmi2TypesPlatform.h",
)


def test_fmi2_headers_are_the_standard_set() -> None:
    """Drift caught: a header renamed, dropped, or shipped as a non-file."""
    headers = pyfmi_sysml2.fmi2_headers()
    assert tuple(header.name for header in headers) == EXPECTED
    assert all(header.is_file() for header in headers)


def test_fmi2_headers_declare_the_public_fmi_api() -> None:
    """Drift caught: the bundled headers are not the FMI C API."""
    text = "".join(
        header.read_text(encoding="utf-8")
        for header in pyfmi_sysml2.fmi2_headers()
    )
    for symbol in ("fmi2Instantiate", "fmi2DoStep", "fmi2GetReal", "fmi2SetReal"):
        assert symbol in text
