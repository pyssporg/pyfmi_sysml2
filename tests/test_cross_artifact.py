"""Cross-artifact consistency gate for one generated FMI component.

The three generators are exercised separately elsewhere; this module asks the
only question that matters for a consumer: after the modelDescription, the C
header, and the FMU archive are written to disk, do they still describe the
same component?

Nothing here compares against a stored golden. The artifacts are read back with
*independent* parsers -- the ``pyssp_standard`` FMI 2 codec and
``xml.etree.ElementTree`` for the XML, regular expressions for the header, and
``zipfile`` for the archive -- and then checked against each other. The gate is
a plain function, :func:`check_artifacts`, so the mutation tests at the bottom
prove it has teeth by feeding it deliberately broken copies.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest
import pycps_sysml2
from pyssp_standard.standard.fmi2.codec import Fmi2ModelDescriptionXmlCodec

from conftest import GENERATION_TIME, fixture_path
from pyfmi_sysml2.c_interface import generate_c_headers
from pyfmi_sysml2.model_description import generate_model_description
from pyfmi_sysml2.package import package_fmu

pytestmark = pytest.mark.contract

SUBJECTS = ("bus", "controller", "generator", "minimal", "sensor")

#: Frames the value-reference enum of a component header.
_ENUM = re.compile(
    r"^typedef enum (?P<stem>\w+)_ValueReference \{\n(?P<body>.*?)\n\} ",
    re.MULTILINE | re.DOTALL,
)

#: The common header a component header includes; its prefix names the package.
_INCLUDE = re.compile(
    r'^#include "(?P<package>.+)_InterfaceCommon\.h"$', re.MULTILINE
)

#: One ``initialize_vr_map`` assignment line.
_INITIALIZER = re.compile(
    r"^  instance->vr_map\[(?P<entry>\w+)\] = "
    r"\{&instance->(?P<member>[^,]+), (?P<tag>\w+), (?P<writable>true|false)\};$",
    re.MULTILINE,
)

#: FMI primitive to the ``<PKG>_DATA_*`` suffix the header maps it to.
_DATA_TAGS = {
    "Real": "REAL",
    "Integer": "INTEGER",
    "Boolean": "BOOLEAN",
    "String": "STRING",
}

#: Fake shared-library payload; the packager copies bytes and never inspects them.
_BINARY_BYTES = b"\x7fELF\x02\x01\x01\x00" + bytes(range(57))

_CODEC = Fmi2ModelDescriptionXmlCodec()


class ArtifactMismatch(ValueError):
    """The artifacts written for one component disagree with each other."""


def _sanitize(text: str) -> str:
    """The header's C identifier spelling of a variable name.

    Re-implemented here rather than imported from the generator: the reading
    side of the gate must not share code with the writing side.
    """
    return re.sub(r"[^0-9A-Za-z]", "_", text).upper()


def _parse_header(
    text: str,
) -> tuple[str, str, list[tuple[str, int]], list[tuple[str, str, str, bool]]]:
    """Read a component header by text: ``(package, stem, enum, initializers)``.

    ``stem`` is ``<Package>_<Component>``; ``enum`` is ``(label, value)`` in
    declaration order; each initializer is ``(entry, member, tag, writable)``.
    """
    match = _ENUM.search(text)
    if match is None:
        raise ArtifactMismatch(
            "header has no <Package>_<Component>_ValueReference enum"
        )
    include = _INCLUDE.search(text)
    if include is None:
        raise ArtifactMismatch("header does not include <Package>_InterfaceCommon.h")

    enumerators: list[tuple[str, int]] = []
    for line in match.group("body").splitlines():
        label, separator, value = line.strip().rstrip(",").partition(" = ")
        if not separator:
            raise ArtifactMismatch(f"malformed value-reference enum line: {line!r}")
        enumerators.append((label, int(value)))

    initializers = [
        (
            found.group("entry"),
            found.group("member"),
            found.group("tag"),
            found.group("writable") == "true",
        )
        for found in _INITIALIZER.finditer(text)
    ]
    return (
        include.group("package"),
        match.group("stem"),
        enumerators,
        initializers,
    )


def _unknown_indices(root: ET.Element, path: str) -> list[int]:
    """The ``index`` attributes under one ModelStructure list, in order."""
    found: list[int] = []
    for unknown in root.findall(path):
        value = unknown.get("index")
        if value is None:
            raise ArtifactMismatch(f"{path} has an Unknown without an index")
        found.append(int(value))
    return found


def check_artifacts(
    xml_text: str,
    header_text: str,
    zip_path: str | Path,
    *,
    platform: str = "linux64",
) -> None:
    """Assert that one component's XML, header, and FMU agree.

    Raises:
        ArtifactMismatch: the artifacts disagree. The message names the check
            that failed: ``XML readers``, ``VR set``, ``VR order``,
            ``modelIdentifier``, ``ModelStructure``, ``archived
            modelDescription``, or ``initialize_vr_map``.
    """
    document = _CODEC.parse(xml_text)
    root = ET.fromstring(xml_text)

    # --- two XML readers must see the same variable list ---------------------
    scalars = root.findall("ModelVariables/ScalarVariable")
    elements: list[tuple[str, int]] = []
    for scalar in scalars:
        name = scalar.get("name")
        reference = scalar.get("valueReference")
        if name is None or reference is None:
            raise ArtifactMismatch(
                "ScalarVariable without a name or valueReference: "
                f"{scalar.attrib}"
            )
        elements.append((name, int(reference)))

    parsed = [(variable.name, variable.value_reference) for variable in document.variables]
    if parsed != elements:
        raise ArtifactMismatch(
            "XML readers disagree on the variable list: "
            f"codec {parsed} vs ElementTree {elements}"
        )

    references = [value for _, value in elements]
    if len(set(references)) != len(references):
        raise ArtifactMismatch(f"duplicate valueReference in modelDescription: {references}")

    # --- header enum vs modelDescription value references --------------------
    package, stem, enumerators, initializers = _parse_header(header_text)
    labels = [label for label, _ in enumerators]
    values = [value for _, value in enumerators]

    if sorted(values) != sorted(references):
        raise ArtifactMismatch(
            f"VR set mismatch: modelDescription {sorted(references)} vs "
            f"header {sorted(values)}"
        )

    expected = [f"{_sanitize(stem)}_VR_{_sanitize(name)}" for name, _ in elements]
    if values != references or labels != expected:
        raise ArtifactMismatch(
            f"VR order mismatch: header {labels} vs modelDescription {expected}"
        )

    # --- archive layout, identifier chain, and archived XML -----------------
    archive = Path(zip_path)
    with zipfile.ZipFile(archive) as bundle:
        entries = bundle.namelist()
        if "modelDescription.xml" not in entries:
            raise ArtifactMismatch(f"{archive} has no modelDescription.xml: {entries}")

        binaries = [
            entry for entry in entries if entry.startswith(f"binaries/{platform}/")
        ]
        if len(binaries) != 1:
            raise ArtifactMismatch(
                f"{archive} must carry exactly one binary under "
                f"binaries/{platform}/: {binaries}"
            )
        binary = Path(binaries[0]).name

        capabilities = document.capabilities
        identifier = capabilities.model_identifier if capabilities else None
        if identifier != Path(binary).stem:
            raise ArtifactMismatch(
                f"modelIdentifier {identifier!r} does not match binary stem "
                f"{Path(binary).stem!r}"
            )
        # A direct FMU model uses its bare definition name for modelName; a
        # container root uses ``<system>.<component>``.
        direct = document.model_name == identifier
        expected_stem = (
            identifier if direct else f"{package}_{identifier}"
        )
        if identifier is None or stem != expected_stem:
            raise ArtifactMismatch(
                f"modelIdentifier {identifier!r} does not match the header "
                f"component: {stem!r} != {expected_stem!r}"
            )

        header_entry = f"sources/{stem}.h"
        if header_entry not in entries:
            raise ArtifactMismatch(f"{archive} has no {header_entry}: {entries}")
        if bundle.read(header_entry) != header_text.encode("utf-8"):
            raise ArtifactMismatch(
                f"{header_entry} in {archive} is not byte-identical to the "
                "generated header"
            )

        archived = _CODEC.parse(bundle.read("modelDescription.xml").decode("utf-8"))

    archived_variables = [
        (variable.name, variable.value_reference) for variable in archived.variables
    ]
    if archived_variables != parsed:
        raise ArtifactMismatch(
            "archived modelDescription differs from the generated one: "
            f"{archived_variables} vs {parsed}"
        )

    # --- ModelStructure vs the declared causalities -------------------------
    outputs = [
        position
        for position, scalar in enumerate(scalars, start=1)
        if scalar.get("causality") == "output"
    ]
    declared = _unknown_indices(root, "ModelStructure/Outputs/Unknown")
    initial = _unknown_indices(root, "ModelStructure/InitialUnknowns/Unknown")

    if sorted(declared) != sorted(outputs):
        extra = sorted(set(declared) - set(outputs))
        missing = sorted(set(outputs) - set(declared))
        raise ArtifactMismatch(
            f"ModelStructure mismatch: Outputs {declared} vs causality=output "
            f"variables at {outputs} (extra {extra}, missing {missing})"
        )
    if sorted(initial) != sorted(declared):
        raise ArtifactMismatch(
            f"ModelStructure mismatch: InitialUnknowns {initial} vs "
            f"Outputs {declared}"
        )

    structure = document.model_structure
    if structure is None:
        raise ArtifactMismatch("modelDescription has no ModelStructure element")
    if [unknown.index for unknown in structure.outputs] != declared:
        raise ArtifactMismatch(
            "ModelStructure mismatch: codec and ElementTree read different "
            f"Outputs {[unknown.index for unknown in structure.outputs]} vs {declared}"
        )
    if [unknown.index for unknown in structure.initial_unknowns] != initial:
        raise ArtifactMismatch(
            "ModelStructure mismatch: codec and ElementTree read different "
            "InitialUnknowns"
        )

    # --- initialize_vr_map: order, storage tag, and writability -------------
    if len(initializers) != len(enumerators):
        raise ArtifactMismatch(
            f"initialize_vr_map assigns {len(initializers)} entries, enum "
            f"declares {len(enumerators)}"
        )
    assigned = [entry for entry, _, _, _ in initializers]
    if assigned != labels:
        raise ArtifactMismatch(
            f"initialize_vr_map order mismatch: {assigned} vs enum {labels}"
        )

    for index, (entry, member, tag, writable) in enumerate(initializers):
        variable = document.variables[index]
        expected_writable = variable.causality != "output"
        expected_tag = _DATA_TAGS.get(variable.type_name, "REAL")
        if writable != expected_writable or tag.rsplit("_", 1)[-1] != expected_tag:
            raise ArtifactMismatch(
                f"initialize_vr_map mapping mismatch for {variable.name!r}: "
                f"{entry} -> (&instance->{member}, {tag}, "
                f"{str(writable).lower()})"
            )


@dataclass(frozen=True)
class Artifacts:
    """One component's three generated artifacts."""

    model_description: Path
    header: Path
    fmu: Path


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_artifacts(directory: Path, subject: str) -> Artifacts:
    """Generate the modelDescription, header, and FMU of one fixture."""
    source = fixture_path(subject, f"{subject}.sysml")

    written = generate_model_description(
        source,
        directory / "model-description",
        generation_time=GENERATION_TIME,
    )
    if len(written) != 1:
        raise AssertionError(
            f"{subject} must export exactly one component, got {len(written)}"
        )
    description = written[0]
    component = description.parent.name

    headers = generate_c_headers(source, directory / "headers")
    package = pycps_sysml2.load(source).package_name
    stems = {f"{package}_{component}", component}
    matching = [path for path in headers if path.stem in stems]
    if len(matching) != 1:
        raise AssertionError(
            f"no single component header for {component} in "
            f"{[path.name for path in headers]}"
        )
    header = matching[0]

    binary = directory / "binaries" / "linux64" / f"{component}.so"
    binary.parent.mkdir(parents=True, exist_ok=True)
    binary.write_bytes(_BINARY_BYTES)

    fmu = package_fmu(
        directory / f"{component}.fmu",
        model_description=description,
        binary=binary,
        headers=[header],
    )
    return Artifacts(description, header, fmu)


def _gate(artifacts: Artifacts) -> None:
    check_artifacts(
        _read(artifacts.model_description),
        _read(artifacts.header),
        artifacts.fmu,
    )


def _rename_entry(source: Path, destination: Path, old: str, new: str) -> None:
    """Copy an archive, renaming one entry and preserving every other byte."""
    with (
        zipfile.ZipFile(source) as original,
        zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as copy,
    ):
        for info in original.infolist():
            name = new if info.filename == old else info.filename
            copy.writestr(name, original.read(info.filename))


def _compiler(name: str) -> str:
    found = shutil.which(name)
    if found is None:
        pytest.skip(f"{name} is not installed")
    return found


def _mutated_xml(artifacts: Artifacts, mutate) -> str:
    """Apply ``mutate`` to the parsed XML and return the serialized result."""
    root = ET.fromstring(_read(artifacts.model_description))
    mutate(root)
    return ET.tostring(root, encoding="unicode")


@pytest.mark.parametrize("subject", SUBJECTS)
def test_generated_artifacts_agree(subject: str, tmp_path: Path) -> None:
    artifacts = build_artifacts(tmp_path, subject)
    _gate(artifacts)

    document = _CODEC.parse(_read(artifacts.model_description))
    assert document.variables, "the gate needs at least one variable"
    structure = document.model_structure
    assert structure is not None and structure.outputs, (
        "the gate needs at least one output to exercise ModelStructure"
    )


@pytest.mark.parametrize("subject", SUBJECTS)
def test_gate_rejects_dropped_scalar_variable(
    subject: str, tmp_path: Path
) -> None:
    artifacts = build_artifacts(tmp_path, subject)
    _gate(artifacts)

    def drop_second(root: ET.Element) -> None:
        variables = root.find("ModelVariables")
        assert variables is not None
        scalars = variables.findall("ScalarVariable")
        assert len(scalars) >= 2
        variables.remove(scalars[1])

    with pytest.raises(ArtifactMismatch, match="VR set mismatch"):
        check_artifacts(
            _mutated_xml(artifacts, drop_second),
            _read(artifacts.header),
            artifacts.fmu,
        )


@pytest.mark.parametrize("subject", SUBJECTS)
def test_gate_rejects_dropped_header_enumerator(
    subject: str, tmp_path: Path
) -> None:
    artifacts = build_artifacts(tmp_path, subject)
    _gate(artifacts)

    header = _read(artifacts.header)
    match = _ENUM.search(header)
    assert match is not None
    lines = match.group("body").splitlines()
    assert len(lines) >= 2
    lines.pop(0)
    mutated = header[: match.start("body")] + "\n".join(lines) + header[match.end("body"):]

    with pytest.raises(ArtifactMismatch, match="VR set mismatch"):
        check_artifacts(_read(artifacts.model_description), mutated, artifacts.fmu)


@pytest.mark.parametrize("subject", SUBJECTS)
def test_gate_rejects_renamed_model_identifier(
    subject: str, tmp_path: Path
) -> None:
    artifacts = build_artifacts(tmp_path, subject)
    _gate(artifacts)

    text = _read(artifacts.model_description)
    found = re.search(r'modelIdentifier="(?P<id>[^"]+)"', text)
    assert found is not None
    identifier = found.group("id")
    mutated = text.replace(
        f'modelIdentifier="{identifier}"',
        f'modelIdentifier="{identifier}X"',
        1,
    )
    assert mutated != text

    with pytest.raises(ArtifactMismatch, match="modelIdentifier"):
        check_artifacts(mutated, _read(artifacts.header), artifacts.fmu)


@pytest.mark.parametrize("subject", SUBJECTS)
def test_gate_rejects_renamed_binary(subject: str, tmp_path: Path) -> None:
    artifacts = build_artifacts(tmp_path, subject)
    _gate(artifacts)

    with zipfile.ZipFile(artifacts.fmu) as bundle:
        binaries = [
            entry for entry in bundle.namelist() if entry.startswith("binaries/")
        ]
    assert len(binaries) == 1
    current = binaries[0]
    stem = Path(current).stem
    renamed = current.replace(f"/{stem}.so", f"/{stem}X.so")
    assert renamed != current

    mutated = tmp_path / "renamed.fmu"
    _rename_entry(artifacts.fmu, mutated, current, renamed)

    with pytest.raises(ArtifactMismatch, match="modelIdentifier"):
        check_artifacts(
            _read(artifacts.model_description),
            _read(artifacts.header),
            mutated,
        )


@pytest.mark.parametrize("subject", SUBJECTS)
def test_gate_rejects_output_causality_flip(
    subject: str, tmp_path: Path
) -> None:
    artifacts = build_artifacts(tmp_path, subject)
    _gate(artifacts)

    def flip_first_output(root: ET.Element) -> None:
        for scalar in root.findall("ModelVariables/ScalarVariable"):
            if scalar.get("causality") == "output":
                scalar.set("causality", "input")
                return
        raise AssertionError("fixture has no output to flip")

    with pytest.raises(ArtifactMismatch, match="ModelStructure mismatch"):
        check_artifacts(
            _mutated_xml(artifacts, flip_first_output),
            _read(artifacts.header),
            artifacts.fmu,
        )


@pytest.mark.parametrize("subject", SUBJECTS)
def test_headers_compile(subject: str, tmp_path: Path) -> None:
    """The emitted headers stay valid C11 and C++17 after all three gates."""
    gcc = _compiler("gcc")
    gxx = _compiler("g++")

    written = generate_c_headers(fixture_path(subject, f"{subject}.sysml"), tmp_path)
    includes = "\n".join(f'#include "{path.name}"' for path in written)

    counters: list[str] = []
    instances: list[str] = []
    for path in written[1:]:
        text = _read(path)
        found = re.search(
            r"inline void (\w+_initialize_vr_map)\((\w+)\* instance\)", text
        )
        assert found is not None, f"no initialize_vr_map in {path.name}"
        counter = re.search(r"enum \{ (\w+_VrCount) = \d+ \};", text)
        assert counter is not None, f"no VrCount in {path.name}"
        counters.append(f"(int){counter.group(1)}")
        instances.append(f"  {found.group(2)} value_{len(instances)};\n  {found.group(1)}(&value_{len(instances)});")

    c_source = tmp_path / "trigger.c"
    c_source.write_text(
        f"{includes}\n\nint pyfmi_c_trigger(void) {{\n  return "
        f"{' + '.join(counters) or '0'};\n}}\n",
        encoding="utf-8",
    )
    cpp_source = tmp_path / "trigger.cpp"
    cpp_source.write_text(
        f"{includes}\n\nvoid pyfmi_cpp_trigger() {{\n"
        + "\n".join(instances)
        + "\n  (void)0;\n}\n",
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


def test_case_document_is_complete() -> None:
    path = Path(__file__).resolve().parent / "golden" / "cross-artifact" / "case.md"
    assert path.is_file(), f"missing case document {path}"
    text = _read(path)
    for heading in (
        "# Case:",
        "## Artifacts",
        "## What this case proves",
        "## Update history",
    ):
        assert heading in text, f"missing {heading!r} in {path}"
    for field in (
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
    ):
        assert f"**{field}**" in text, f"missing {field!r} in {path}"
