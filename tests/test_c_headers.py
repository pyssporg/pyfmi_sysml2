"""Golden, structure, and compile gates for the generated C headers.

The headers are split in two: a common header that must be plain C11, and a
per-component header whose C++ block is what an FMI 2.0 host actually fills in.
Both halves are compiled here, because a header that only C++ accepts is the
failure mode the split exists to prevent.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest
from pycps_sysml2 import core_definitions, load

from conftest import GOLDEN_ROOT, fixture_path, update_goldens
from golden_utils import assert_golden_text
from pyfmi_sysml2.c_interface import (
    common_header_name,
    component_header,
    component_header_name,
    generate_c_headers,
    header_stem,
    interface_common_header,
    member_expression,
)
from pyfmi_sysml2.interface import (
    DATA_TYPE_TAGS,
    components,
    export_identity,
    resolve_system,
    sanitize_identifier,
)

pytestmark = pytest.mark.component

SUBJECTS = ("bus", "controller", "generator", "minimal", "sensor")

GOLDEN = GOLDEN_ROOT / "c-headers"

CASE_HEADINGS = (
    "# Case:",
    "## Artifacts",
    "## What this case proves",
    "## Update history",
)

CASE_FIELDS = (
    "Conversion",
    "Requirement / fault",
    "Level",
    "Input",
    "Expected",
    "Independent oracle",
    "Comparison",
    "Normalization",
    "Volatile fields",
    "Update policy",
    "Notes",
)

#: Names from the source architecture this repository was ported from.
FORBIDDEN_NAMES = ("Aircraft", "FuelSystem", "FlightGearBridge")

_ENUM_BLOCK = re.compile(
    r"^typedef enum (?P<name>\w+)_ValueReference \{\n(?P<body>.*?)\n\} ",
    re.MULTILINE | re.DOTALL,
)

_ASSIGNMENT = re.compile(
    r"^  instance->vr_map\[(?P<entry>\w+)\] = "
    r"\{&instance->(?P<member>[^,]+), (?P<tag>\w+), (?P<writable>true|false)\};$",
    re.MULTILINE,
)


def _source(subject: str) -> Path:
    return fixture_path(subject, f"{subject}.sysml")


def _generated(subject: str, directory: Path) -> list[Path]:
    return generate_c_headers(_source(subject), directory)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _vr_entries(text: str) -> list[tuple[str, int]]:
    """``(entry, value)`` for every entry of the value-reference enum."""
    match = _ENUM_BLOCK.search(text)
    assert match is not None, "no ValueReference enum"
    entries: list[tuple[str, int]] = []
    for line in match.group("body").splitlines():
        label, _, value = line.strip().rstrip(",").partition(" = ")
        entries.append((label, int(value)))
    return entries


def _outside_cpp_block(text: str) -> str:
    """``text`` with the ``#ifdef __cplusplus`` section removed."""
    start = text.find("#ifdef __cplusplus")
    if start == -1:
        return text
    end = text.find("#endif  /* __cplusplus */", start)
    assert end != -1, "unterminated __cplusplus block"
    return text[:start] + text[end:]


@pytest.mark.parametrize("subject", SUBJECTS)
def test_headers_match_golden(subject: str, tmp_path: Path) -> None:
    written = _generated(subject, tmp_path)
    names = [path.name for path in written]

    assert names[0] == common_header_name(load(_source(subject)).package_name)
    assert names[1:] == sorted(names[1:])

    golden = sorted(path.name for path in (GOLDEN / subject).glob("*.h"))
    if not update_goldens():
        assert sorted(names) == golden

    for path in written:
        assert_golden_text(GOLDEN / subject / path.name, _text(path))


@pytest.mark.parametrize("subject", SUBJECTS)
def test_text_builders_match_written_files(subject: str, tmp_path: Path) -> None:
    architecture = load(_source(subject))
    package = architecture.package_name
    direct = export_identity(architecture, resolve_system(architecture)).direct
    exported = components(architecture)
    written = {path.name: _text(path) for path in _generated(subject, tmp_path)}

    assert written[common_header_name(package)] == interface_common_header(
        package, exported
    )
    for item in exported:
        assert written[
            component_header_name(package, item.name, direct=direct)
        ] == component_header(package, item, direct=direct)


@pytest.mark.parametrize("subject", SUBJECTS)
def test_header_boundaries(subject: str, tmp_path: Path) -> None:
    written = _generated(subject, tmp_path)
    common = _text(written[0])
    assert common.endswith("\n")
    for path in written[1:]:
        assert not _text(path).endswith("\n")


@pytest.mark.parametrize("subject", SUBJECTS)
def test_vr_enum_matches_component_variables(subject: str, tmp_path: Path) -> None:
    architecture = load(_source(subject))
    package = architecture.package_name
    written = _generated(subject, tmp_path)
    texts = {path.name: _text(path) for path in written}

    direct = export_identity(architecture, resolve_system(architecture)).direct
    for item in components(architecture):
        text = texts[component_header_name(package, item.name, direct=direct)]
        entries = _vr_entries(text)
        stem = sanitize_identifier(
            header_stem(package, item.name, direct=direct)
        )

        assert [value for _, value in entries] == [
            variable.value_reference for variable in item.variables
        ]
        assert [label for label, _ in entries] == [
            f"{stem}_VR_{sanitize_identifier(variable.name)}"
            for variable in item.variables
        ]
        assert len({label for label, _ in entries}) == item.vr_count


@pytest.mark.parametrize("subject", SUBJECTS)
def test_writability_follows_causality(subject: str, tmp_path: Path) -> None:
    architecture = load(_source(subject))
    package = architecture.package_name
    written = _generated(subject, tmp_path)
    texts = {path.name: _text(path) for path in written}

    direct = export_identity(architecture, resolve_system(architecture)).direct
    for item in components(architecture):
        text = texts[component_header_name(package, item.name, direct=direct)]
        entries = [label for label, _ in _vr_entries(text)]
        assignments = {
            match.group("entry"): (
                match.group("member"),
                match.group("tag"),
                match.group("writable"),
            )
            for match in _ASSIGNMENT.finditer(text)
        }

        assert list(assignments) == entries
        stem = sanitize_identifier(
            header_stem(package, item.name, direct=direct)
        )
        for variable in item.variables:
            member, tag, writable = assignments[
                f"{stem}_VR_{sanitize_identifier(variable.name)}"
            ]
            assert member == member_expression(variable.member)
            assert tag == (
                f"{sanitize_identifier(package)}_DATA_"
                f"{DATA_TYPE_TAGS[variable.type_name]}"
            )
            assert writable == ("true" if variable.causality != "output" else "false")


@pytest.mark.parametrize("subject", SUBJECTS)
def test_common_header_is_c_valid(subject: str, tmp_path: Path) -> None:
    written = _generated(subject, tmp_path)
    common = _text(written[0])
    package = load(_source(subject)).package_name

    cpp_at = common.find("#ifdef __cplusplus")
    assert cpp_at == -1 or cpp_at > common.index(f"{package}_VrMapping")
    assert "nullptr" not in common
    assert "= {}" not in common
    assert "#include <stdbool.h>" in common
    assert "#include <stddef.h>" in common
    assert "#include <stdint.h>" in common
    assert f"#ifndef {sanitize_identifier(package)}_INTERFACECOMMON_H" in common
    assert "void* data;" in common
    assert "bool writable;" in common

    for path in written[1:]:
        outside = _outside_cpp_block(_text(path))
        assert "nullptr" not in outside
        assert "= {}" not in outside
        assert "std::string" not in outside


@pytest.mark.parametrize("subject", SUBJECTS)
def test_no_source_specific_names(subject: str, tmp_path: Path) -> None:
    for path in _generated(subject, tmp_path):
        text = _text(path)
        for name in FORBIDDEN_NAMES:
            assert name not in text


@pytest.mark.parametrize("subject", SUBJECTS)
def test_case_document_is_complete(subject: str) -> None:
    path = GOLDEN / subject / "case.md"
    assert path.is_file(), f"missing case document {path}"
    text = _text(path)
    for heading in CASE_HEADINGS:
        assert heading in text, f"missing {heading!r} in {path}"
    for field in CASE_FIELDS:
        assert f"**{field}**" in text, f"missing {field!r} in {path}"


def _compiler(name: str) -> str:
    found = shutil.which(name)
    if found is None:
        pytest.skip(f"{name} is not installed")
    return found


def _instance(name: str) -> str:
    return f"instance_{name.lower()}"


@pytest.mark.parametrize("subject", SUBJECTS)
def test_headers_compile(subject: str, tmp_path: Path) -> None:
    """The common header is C11; the instance helper is C++17."""
    gcc = _compiler("gcc")
    gxx = _compiler("g++")

    written = _generated(subject, tmp_path)
    names = [path.name for path in written]
    architecture = load(_source(subject))
    package = architecture.package_name
    items = components(architecture)
    direct = export_identity(architecture, resolve_system(architecture)).direct

    includes = "\n".join(f'#include "{name}"' for name in names)
    stems = [
        header_stem(package, item.name, direct=direct) for item in items
    ]
    vr_counts = " + ".join(f"(int){stem}_VrCount" for stem in stems) or "0"

    c_source = tmp_path / "trigger.c"
    c_source.write_text(
        f"{includes}\n\nint pyfmi_c_trigger(void) {{\n  return {vr_counts};\n}}\n",
        encoding="utf-8",
    )

    cpp_body = "\n".join(
        f"  {stem}_Instance {_instance(item.name)};\n"
        f"  {stem}_initialize_vr_map(&{_instance(item.name)});"
        for item, stem in zip(items, stems)
    )
    cpp_source = tmp_path / "trigger.cpp"
    cpp_source.write_text(
        f"{includes}\n\nvoid pyfmi_cpp_trigger() {{\n{cpp_body}\n"
        "  (void)0;\n}\n",
        encoding="utf-8",
    )

    for command in (
        [gcc, "-std=c11", "-fsyntax-only", "-I", str(tmp_path), str(c_source)],
        [gxx, "-std=c++17", "-fsyntax-only", "-I", str(tmp_path), str(cpp_source)],
    ):
        result = subprocess.run(command, capture_output=True, text=True)
        assert result.returncode == 0, (
            f"{' '.join(command)}\n{result.stdout}{result.stderr}"
        )


def test_prefix_overrides_file_and_type_names(tmp_path: Path) -> None:
    written = generate_c_headers(
        _source("minimal"), tmp_path, prefix="Custom"
    )

    assert [path.name for path in written] == [
        "Custom_InterfaceCommon.h",
        "Custom_Scale.h",
    ]
    component = _text(written[1])
    assert "typedef enum Custom_Scale_ValueReference {" in component
    assert "struct Custom_Scale_Instance {" in component


def test_composition_selects_the_exported_root(tmp_path: Path) -> None:
    written = generate_c_headers(
        _source("controller"), tmp_path, composition="ControllerComposition"
    )
    assert [path.name for path in written] == [
        "Controller_InterfaceCommon.h",
        "Controller_Controller.h",
    ]


def test_direct_fmu_model_is_the_export_unit(tmp_path: Path) -> None:
    """A marked definition needs no container root; it exports itself."""
    architecture = load(_source("generator"))

    system = resolve_system(architecture)
    exported = components(architecture)

    assert system.name == "Generator"
    assert [item.name for item in exported] == ["Generator"]
    assert [item.name for item in components(architecture, composition="Generator")] == [
        "Generator"
    ]
    assert [path.name for path in generate_c_headers(architecture, tmp_path)] == [
        "Generator_InterfaceCommon.h",
        "Generator.h",
    ]


def test_direct_fmu_model_header_is_not_doubled(tmp_path: Path) -> None:
    """The package name is not repeated in the direct component header."""
    [common, component] = generate_c_headers(_source("generator"), tmp_path)
    text = _text(component)

    assert common.name == "Generator_InterfaceCommon.h"
    assert component.name == "Generator.h"
    assert "typedef enum Generator_ValueReference {" in text
    assert "enum { Generator_VrCount = 3 };" in text
    assert "struct Generator_Instance {" in text
    assert "Generator_Generator" not in text
    assert "Generator_Generator" not in _text(common)


def test_marker_definition_is_not_an_export_candidate(tmp_path: Path) -> None:
    """``part def FmuModel;`` from the core is a role marker, not a component."""
    architecture = tmp_path / "plain.sysml"
    architecture.write_text(
        """package Plain {
  port def Signal {
    attribute value : Real;
  }

  part def Leaf {
    out port y : Signal;
  }

  part def PlainComposition {
    part leaf : Leaf;
  }
}
""",
        encoding="utf-8",
    )

    loaded = load(architecture, core_definitions())

    assert resolve_system(loaded).name == "PlainComposition"
    assert [item.name for item in components(loaded)] == ["Leaf"]


def test_several_fmu_models_require_a_name(tmp_path: Path) -> None:
    """Two marked definitions are as ambiguous as two container roots."""
    architecture = tmp_path / "pair.sysml"
    architecture.write_text(
        """package Pair {
  part def FmuModel;

  port def Signal {
    attribute value : Real;
  }

  part def Alpha :> FmuModel {
    out port y : Signal;
  }

  part def Zulu :> FmuModel {
    out port y : Signal;
  }
}
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Cannot pick a composition root") as found:
        components(load(architecture))

    message = str(found.value)
    assert "2 FmuModel candidates" in message
    assert "Alpha" in message
    assert "Zulu" in message


def test_accepts_an_architecture_object(tmp_path: Path) -> None:
    architecture = load(_source("bus"))
    from_object = generate_c_headers(architecture, tmp_path / "object")
    from_path = generate_c_headers(_source("bus"), tmp_path / "path")

    assert [path.name for path in from_object] == [path.name for path in from_path]
    for left, right in zip(from_object, from_path):
        assert _text(left) == _text(right)


def test_member_expression_escapes_keywords() -> None:
    assert member_expression("command.auto") == "command.auto_"
    assert member_expression("gains[0]") == "gains[0]"
    assert member_expression("p.x") == "p.x"
    assert member_expression("class[1].new") == "class_[1].new_"
