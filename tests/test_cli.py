"""System tests for the ``pyfmi`` command line.

Every case drives ``main`` the way the console script does, with a temporary
output root. The CLI is thin, so these tests pin the shell contract rather than
the artifact contents: exit codes, one stdout line per written path, stderr
without a traceback, and the files the subcommands claim to have written.
"""

from __future__ import annotations

import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from conftest import GENERATION_TIME_TEXT, GOLDEN_ROOT, fixture_path
from pyfmi_sysml2.cli import main

pytestmark = pytest.mark.system


def _source(subject: str) -> Path:
    return fixture_path(subject, f"{subject}.sysml").resolve()


def test_model_description_subcommand(tmp_path: Path, capsys) -> None:
    output = tmp_path / "build"

    assert main(["model-description", str(_source("sensor")), "-o", str(output)]) == 0

    description = output / "Tank" / "modelDescription.xml"
    assert description.is_file()
    assert '<CoSimulation modelIdentifier="Tank"' in description.read_text(
        encoding="utf-8"
    )
    assert capsys.readouterr().out.splitlines() == [str(description)]


def test_c_headers_subcommand(tmp_path: Path, capsys) -> None:
    output = tmp_path / "headers"

    assert main(["c-headers", str(_source("controller")), "-o", str(output)]) == 0

    common = output / "Controller_InterfaceCommon.h"
    component = output / "Controller_Controller.h"
    assert common.is_file()
    assert component.is_file()
    assert "Controller_ValueReference" in component.read_text(encoding="utf-8")
    assert capsys.readouterr().out.splitlines() == [str(common), str(component)]


def test_modelica_subcommand(tmp_path: Path, capsys) -> None:
    output = tmp_path / "modelica"

    assert main(["modelica", str(_source("sensor")), "-o", str(output)]) == 0

    root = output / "GeneratedInterfaces"
    expected = [
        root / "GeneratedInterfaces.mo",
        root / "Interfaces.mo",
        root / "package.mo",
        root / "package.order",
    ]
    assert all(path.is_file() for path in expected)
    assert capsys.readouterr().out.splitlines() == [
        str(path) for path in expected
    ]


def test_generation_time_reproduces_the_golden_bytes(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    argv = [
        "model-description",
        str(_source("sensor")),
        "--generation-time",
        GENERATION_TIME_TEXT,
    ]

    assert main([*argv, "-o", str(first)]) == 0
    assert main([*argv, "-o", str(second)]) == 0

    produced = first / "Tank" / "modelDescription.xml"
    golden = (
        GOLDEN_ROOT
        / "model-description"
        / "sensor"
        / "Tank"
        / "modelDescription.xml"
    )
    assert produced.read_bytes() == golden.read_bytes()
    assert (
        second / "Tank" / "modelDescription.xml"
    ).read_bytes() == produced.read_bytes()


def test_component_filter_writes_one_file(tmp_path: Path) -> None:
    output = tmp_path / "selected"

    assert (
        main(
            [
                "model-description",
                str(_source("sensor")),
                "-o",
                str(output),
                "--component",
                "Tank",
            ]
        )
        == 0
    )

    assert [
        path.relative_to(output).as_posix()
        for path in output.rglob("modelDescription.xml")
    ] == ["Tank/modelDescription.xml"]


def test_package_subcommand_writes_an_fmu(tmp_path: Path) -> None:
    source = _source("minimal")
    build = tmp_path / "build"
    assert main(["model-description", str(source), "-o", str(build)]) == 0
    assert main(["c-headers", str(source), "-o", str(build)]) == 0

    description = build / "Scale" / "modelDescription.xml"
    binary = tmp_path / "lib" / "Scale.so"
    binary.parent.mkdir()
    binary.write_bytes(b"\x7fELF\x02\x01\x01\x00")

    archive = tmp_path / "Scale.fmu"
    argv = [
        "package",
        "-o",
        str(archive),
        "--model-description",
        str(description),
        "--binary",
        str(binary),
    ]
    for header in sorted(build.glob("*.h")):
        argv.extend(["--header", str(header)])

    assert main(argv) == 0

    assert archive.is_file()
    with zipfile.ZipFile(archive) as bundle:
        names = bundle.namelist()
    assert "modelDescription.xml" in names
    assert "binaries/linux64/Scale.so" in names
    assert "sources/Minimal_InterfaceCommon.h" in names


@pytest.mark.parametrize(
    "command",
    [None, "model-description", "c-headers", "modelica", "package"],
)
def test_help_succeeds_and_mentions_the_output(command, capsys) -> None:
    argv = ["--help"] if command is None else [command, "--help"]

    with pytest.raises(SystemExit) as raised:
        main(argv)

    assert raised.value.code == 0
    assert "output" in capsys.readouterr().out


def test_default_output_is_build(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    assert main(["model-description", str(_source("sensor"))]) == 0

    assert (tmp_path / "build" / "Tank" / "modelDescription.xml").is_file()


def test_missing_source_is_reported_without_a_traceback(
    tmp_path: Path, capsys
) -> None:
    absent = tmp_path / "absent.sysml"

    assert main(["model-description", str(absent)]) == 1

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "pyfmi:" in captured.err
    assert "absent.sysml" in captured.err
    assert "Traceback" not in captured.err


@pytest.mark.parametrize(
    "value", ["2026-01-01T00:00:00", "yesterday"]
)
def test_bad_generation_time_is_a_usage_error(
    value: str, tmp_path: Path, capsys
) -> None:
    with pytest.raises(SystemExit) as raised:
        main(
            [
                "model-description",
                str(_source("sensor")),
                "-o",
                str(tmp_path),
                "--generation-time",
                value,
            ]
        )

    assert raised.value.code == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "--generation-time" in captured.err
    assert "Traceback" not in captured.err


def test_missing_binary_is_reported_without_a_traceback(
    tmp_path: Path, capsys
) -> None:
    build = tmp_path / "build"
    assert main(["model-description", str(_source("minimal")), "-o", str(build)]) == 0
    capsys.readouterr()

    assert (
        main(
            [
                "package",
                "-o",
                str(tmp_path / "Scale.fmu"),
                "--model-description",
                str(build / "Scale" / "modelDescription.xml"),
                "--binary",
                str(tmp_path / "absent.so"),
            ]
        )
        == 1
    )

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "pyfmi:" in captured.err
    assert "absent.so" in captured.err
    assert "Traceback" not in captured.err


def test_console_script_is_installed() -> None:
    executable = Path(sys.executable).with_name("pyfmi")
    assert executable.is_file(), f"missing console script {executable}"

    result = subprocess.run(
        [str(executable), "--help"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "usage: pyfmi" in result.stdout
