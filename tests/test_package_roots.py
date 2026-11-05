"""Two-root load: an included definition with parts is not a composition root.

``pycps_sysml2`` stores a definition of the primary package under its bare name
and a definition of any other package under ``"<package>::<name>"``. Root
selection must compare stored keys on both sides; comparing a bare name against
a stored key counts an included definition with parts as an extra root and
refuses the load as ambiguous.
"""

from __future__ import annotations

import pycps_sysml2
import pytest

from conftest import GENERATION_TIME, fixture_path
from pyfmi_sysml2.c_interface import generate_c_headers
from pyfmi_sysml2.interface import components, resolve_system
from pyfmi_sysml2.model_description import generate_model_description

pytestmark = pytest.mark.component

PRIMARY = fixture_path("packages", "packages.sysml")
INCLUDE = fixture_path("packages", "support")


@pytest.fixture(name="architecture")
def architecture_fixture():
    return pycps_sysml2.load(PRIMARY, INCLUDE)


def test_same_bare_name_coexists_across_packages(architecture):
    assert set(architecture.part_definitions) == {
        "Leaf",
        "PackagesComposition",
        "Support::Leaf",
        "Support::Unit",
    }
    assert architecture.included_definitions == {
        "Support::Leaf",
        "Support::SupportParameters",
        "Support::SupportSignal",
        "Support::Unit",
    }


def test_included_definition_with_parts_is_not_a_second_root(architecture):
    system = resolve_system(architecture)

    assert system.name == "PackagesComposition"
    assert architecture.stored_key(system) == "PackagesComposition"


def test_exported_component_keeps_its_bare_name(architecture):
    exported = components(architecture)

    assert [component.name for component in exported] == ["Leaf"]
    assert [field.name for field in exported[0].parameters] == ["bias"]


def test_artifacts_carry_no_package_qualifier(architecture, tmp_path):
    written = generate_model_description(
        architecture,
        tmp_path / "modelDescription",
        generation_time=GENERATION_TIME,
    )
    headers = generate_c_headers(architecture, tmp_path / "headers")
    paths = [*written, *headers]

    assert "::" not in "".join(path.as_posix() for path in paths)
    assert [path.relative_to(tmp_path).as_posix() for path in paths] == [
        "modelDescription/Leaf/modelDescription.xml",
        "headers/Packages_InterfaceCommon.h",
        "headers/Packages_Leaf.h",
    ]

    xml = written[0].read_text(encoding="utf-8")
    assert 'modelName="PackagesComposition.Leaf"' in xml
    assert 'modelIdentifier="Leaf"' in xml
    assert "::" not in xml

    for header in headers:
        assert "::" not in header.read_text(encoding="utf-8")
