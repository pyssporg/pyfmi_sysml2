"""Component tests for the deterministic FMU packager.

Every case builds its inputs inline: a fake shared library, a generated header,
and a model description written by the ``pyssp_standard`` codec. Nothing here
compiles a binary; the archive layout and its determinism are the unit under
test.
"""

from __future__ import annotations

import hashlib
import os
import zipfile
from dataclasses import dataclass
from pathlib import Path

import pytest
from golden_utils import assert_golden_text
from pyssp_standard.common.archive.archive import package_archive
from pyssp_standard.standard.fmi2.codec import Fmi2ModelDescriptionXmlCodec
from pyssp_standard.standard.fmi2.model.model_description import (
    Fmi2DefaultExperiment,
    Fmi2ElementInfo,
    Fmi2InterfaceAttributes,
    Fmi2ModelDescriptionDocument,
    Fmi2ModelStructure,
    Fmi2ScalarVariable,
    Fmi2Unknown,
)

from pyfmi_sysml2.package import package_fmu, stage_fmu

pytestmark = pytest.mark.component

GOLDEN_ROOT = Path(__file__).resolve().parent / "golden" / "package"

#: Fake ELF payload; the packager copies bytes and never inspects them.
BINARY_BYTES = b"\x7fELF\x02\x01\x01\x00" + bytes(range(57))

_EPOCH = (2000, 1, 1, 0, 0, 0)


def model_description(identifier: str) -> str:
    """A small valid FMI 2.0 CoSimulation description, one input one output."""
    document = Fmi2ModelDescriptionDocument(
        root=Fmi2ElementInfo(tag="fmiModelDescription"),
        fmi_version="2.0",
        model_name=identifier,
        guid="{6ba7b810-9dad-11d1-80b4-00c04fd430c8}",
        generation_tool="pyfmi_sysml2 tests",
        variable_naming_convention="structured",
        default_experiment=Fmi2DefaultExperiment(start_time=0.0, stop_time=1.0),
        interface_type="CoSimulation",
        capabilities=Fmi2InterfaceAttributes(model_identifier=identifier),
        variables=[
            Fmi2ScalarVariable(
                name="u",
                value_reference=0,
                type_name="Real",
                causality="input",
                variability="continuous",
                initial="exact",
            ),
            Fmi2ScalarVariable(
                name="y",
                value_reference=1,
                type_name="Real",
                causality="output",
                variability="continuous",
                initial="calculated",
            ),
        ],
        model_structure=Fmi2ModelStructure(
            outputs=[Fmi2Unknown(index=1)],
            initial_unknowns=[Fmi2Unknown(index=1)],
        ),
    )
    return Fmi2ModelDescriptionXmlCodec().serialize(document)


@dataclass(frozen=True)
class Inputs:
    model_description: Path
    binary: Path
    header: Path
    resource_dir: Path
    resource_file: Path
    documentation: Path


def make_inputs(root: Path, identifier: str) -> Inputs:
    """Write one complete set of packaging inputs under *root*."""
    source = root / "src"
    source.mkdir(parents=True)

    description = source / f"{identifier}.xml"
    description.write_text(model_description(identifier), encoding="utf-8")

    binary = source / f"{identifier}.so"
    binary.write_bytes(BINARY_BYTES)

    header = source / f"{identifier.lower()}.h"
    header.write_text("#pragma once\n", encoding="utf-8")

    resource_dir = source / "data"
    (resource_dir / "nested").mkdir(parents=True)
    (resource_dir / "a.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    (resource_dir / "nested" / "b.csv").write_text("3,4\n", encoding="utf-8")

    resource_file = source / "params.json"
    resource_file.write_text('{"gain": 2.0}\n', encoding="utf-8")

    documentation = source / "reference.txt"
    documentation.write_text("Reference model.\n", encoding="utf-8")

    return Inputs(
        model_description=description,
        binary=binary,
        header=header,
        resource_dir=resource_dir,
        resource_file=resource_file,
        documentation=documentation,
    )


def full_package(output: Path, inputs: Inputs) -> Path:
    return package_fmu(
        output,
        model_description=inputs.model_description,
        binary=inputs.binary,
        headers=[inputs.header],
        resources=[inputs.resource_dir, inputs.resource_file],
        documentation=[inputs.documentation],
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mode_of(info: zipfile.ZipInfo) -> int:
    return (info.external_attr >> 16) & 0o777


def listing(archive: Path) -> str:
    """``zipinfo -l``-style text, with the archive digest for the case record."""
    lines = [
        f"sha256 {sha256(archive)}",
        "mode   size timestamp           name",
    ]
    with zipfile.ZipFile(archive) as bundle:
        for info in bundle.infolist():
            stamp = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(
                *info.date_time
            )
            lines.append(
                f"{mode_of(info):04o} {info.file_size:6d} {stamp} {info.filename}"
            )
    return "\n".join(lines) + "\n"


def test_archive_layout_mode_and_epoch(tmp_path: Path) -> None:
    inputs = make_inputs(tmp_path / "inputs", "Tank")
    archive = full_package(tmp_path / "Tank.fmu", inputs)

    expected = sorted(
        [
            "binaries/linux64/Tank.so",
            "documentation/reference.txt",
            "modelDescription.xml",
            "resources/data/a.csv",
            "resources/data/nested/b.csv",
            "resources/params.json",
            "sources/tank.h",
        ]
    )

    with zipfile.ZipFile(archive) as bundle:
        infos = bundle.infolist()
        assert bundle.namelist() == expected
        assert bundle.namelist()[0] == "binaries/linux64/Tank.so"
        assert "modelDescription.xml" in bundle.namelist()
        assert [info.filename for info in infos] == expected

        for info in infos:
            assert info.date_time == _EPOCH, info.filename
            if info.filename == "binaries/linux64/Tank.so":
                assert mode_of(info) == 0o755
            else:
                assert mode_of(info) == 0o644, info.filename


def test_stage_fmu_sets_executable_bit_on_disk(tmp_path: Path) -> None:
    inputs = make_inputs(tmp_path / "inputs", "Tank")
    stage = stage_fmu(
        tmp_path / "stage",
        model_description=inputs.model_description,
        binary=inputs.binary,
    )

    assert (stage / "modelDescription.xml").is_file()
    staged_binary = stage / "binaries" / "linux64" / "Tank.so"
    assert staged_binary.is_file()
    assert staged_binary.stat().st_mode & 0o111 == 0o111
    assert not (stage / "sources").exists()
    assert not (stage / "resources").exists()
    assert not (stage / "documentation").exists()


def test_stage_fmu_refuses_non_empty_directory(tmp_path: Path) -> None:
    inputs = make_inputs(tmp_path / "inputs", "Tank")
    stage = tmp_path / "stage"
    stage.mkdir()
    (stage / "stale.txt").write_text("old", encoding="utf-8")

    arguments = {
        "model_description": inputs.model_description,
        "binary": inputs.binary,
    }
    with pytest.raises(FileExistsError, match="overwrite=True"):
        stage_fmu(stage, **arguments)

    stage_fmu(stage, overwrite=True, **arguments)
    assert not (stage / "stale.txt").exists()
    assert (stage / "modelDescription.xml").is_file()


def test_repack_is_byte_identical_from_fresh_stages(tmp_path: Path) -> None:
    inputs = make_inputs(tmp_path / "inputs", "Tank")

    first = full_package(tmp_path / "one.fmu", inputs)
    second = full_package(tmp_path / "two.fmu", inputs)

    assert sha256(first) == sha256(second)


def test_mtime_does_not_change_packaged_bytes(tmp_path: Path) -> None:
    inputs = make_inputs(tmp_path / "inputs", "Tank")
    arguments = {
        "model_description": inputs.model_description,
        "binary": inputs.binary,
        "headers": [inputs.header],
        "resources": [inputs.resource_dir, inputs.resource_file],
        "documentation": [inputs.documentation],
    }

    first_stage = stage_fmu(tmp_path / "stage-one", **arguments)
    second_stage = stage_fmu(tmp_path / "stage-two", **arguments)
    for path in sorted(second_stage.rglob("*")):
        if path.is_file():
            os.utime(path, (1_000_000_000, 1_000_000_000))

    # The same archive call package_fmu makes, on stages whose filesystem
    # timestamps differ.
    first = package_archive(first_stage, tmp_path / "one.fmu")
    second = package_archive(second_stage, tmp_path / "two.fmu")

    assert sha256(first) == sha256(second)


def test_resources_and_documentation_are_optional(tmp_path: Path) -> None:
    inputs = make_inputs(tmp_path / "inputs", "Valve")
    archive = package_fmu(
        tmp_path / "minimal.fmu",
        model_description=inputs.model_description,
        binary=inputs.binary,
        headers=[inputs.header],
    )

    with zipfile.ZipFile(archive) as bundle:
        assert bundle.namelist() == [
            "binaries/linux64/Valve.so",
            "modelDescription.xml",
            "sources/valve.h",
        ]


def test_model_identifier_must_match_binary_stem(tmp_path: Path) -> None:
    tank = make_inputs(tmp_path / "tank", "Tank")
    valve = make_inputs(tmp_path / "valve", "Valve")

    with pytest.raises(ValueError, match="modelIdentifier"):
        package_fmu(
            tmp_path / "bad.fmu",
            model_description=valve.model_description,
            binary=tank.binary,
        )


def test_unsupported_platform_names_the_allow_list(tmp_path: Path) -> None:
    inputs = make_inputs(tmp_path / "inputs", "Tank")

    with pytest.raises(ValueError) as error:
        package_fmu(
            tmp_path / "bad.fmu",
            model_description=inputs.model_description,
            binary=inputs.binary,
            platform="windows64",
        )

    message = str(error.value)
    assert "windows64" in message
    assert "linux64" in message


def test_platform_token_rejects_path_separator(tmp_path: Path) -> None:
    inputs = make_inputs(tmp_path / "inputs", "Tank")

    for platform in ("../evil", "linux/64", ".."):
        with pytest.raises(ValueError, match="platform"):
            stage_fmu(
                tmp_path / "stage",
                model_description=inputs.model_description,
                binary=inputs.binary,
                platform=platform,
            )


def test_missing_model_description_is_actionable(tmp_path: Path) -> None:
    inputs = make_inputs(tmp_path / "inputs", "Tank")

    with pytest.raises(ValueError, match="modelDescription"):
        package_fmu(
            tmp_path / "bad.fmu",
            model_description=tmp_path / "absent.xml",
            binary=inputs.binary,
        )


def test_invalid_model_description_is_actionable(tmp_path: Path) -> None:
    inputs = make_inputs(tmp_path / "inputs", "Tank")
    broken = tmp_path / "broken.xml"
    broken.write_text("<fmiModelDescription/>", encoding="utf-8")

    with pytest.raises(ValueError, match="valid FMI 2.0"):
        package_fmu(
            tmp_path / "bad.fmu",
            model_description=broken,
            binary=inputs.binary,
        )


def test_wrong_fmi_version_is_rejected(tmp_path: Path) -> None:
    inputs = make_inputs(tmp_path / "inputs", "Tank")
    legacy = tmp_path / "legacy.xml"
    legacy.write_text(
        model_description("Tank").replace('fmiVersion="2.0"', 'fmiVersion="1.0"'),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="fmiVersion"):
        package_fmu(
            tmp_path / "bad.fmu",
            model_description=legacy,
            binary=inputs.binary,
        )


def test_archive_listing_matches_golden(tmp_path: Path) -> None:
    inputs = make_inputs(tmp_path / "inputs", "Tank")
    archive = full_package(tmp_path / "Tank.fmu", inputs)

    assert_golden_text(GOLDEN_ROOT / "layout" / "listing.txt", listing(archive))
