"""Component tests for the generated Modelica interface package."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from conftest import GOLDEN_ROOT, fixture_path
from golden_utils import assert_golden_text
from pyfmi_sysml2.modelica import generate_modelica

pytestmark = pytest.mark.component

SUBJECTS = ("bus", "controller", "minimal", "sensor")

#: Every file the generator writes, relative to ``<output>/<package>/``.
FILES = ("GeneratedInterfaces.mo", "Interfaces.mo", "package.mo", "package.order")

#: The draft this generator replaces hard-coded these names; none may survive.
FORBIDDEN = ("AircraftCommon", "Aircraft", "FlightGearBridge")

GOLDEN = GOLDEN_ROOT / "modelica"

OMC = Path("/usr/bin/omc")

#: Member lines each fixture must produce, per connector.
CONNECTORS = {
    "bus": {
        "Actuation": [
            "input Real channel_a;",
            "input Real channel_b;",
            "input Real channel_c;",
        ],
        # ``in``, ``out``, and ``inout`` usages cannot agree on a direction.
        "Orientation": ["Real roll;", "Real pitch;", "Real yaw;"],
        "Position": ["Real x;", "Real y;", "Real z;"],
        "StatusPacket": ["output Real speed;", "output Integer health;"],
    },
    "controller": {
        "Command": [
            "input Real manual;",
            "input Real auto;",
            "input Integer mode;",
        ],
        "Status": ["output Integer code;"],
        "Throttle": ["output Real demand;", "output Boolean enabled;"],
    },
    "minimal": {"Signal": ["Real value;"]},
    "sensor": {
        "LevelState": [
            "output Real remaining;",
            "output Real fraction;",
            "output Boolean empty;",
        ],
        "Rate": ["input Real rate;"],
    },
}


def _connectors(path: Path) -> dict[str, list[str]]:
    """Connector name to its member lines, in file order."""
    connectors: dict[str, list[str]] = {}
    current: str | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if current is None and line.startswith("connector ") and "=" not in line:
            current = line.removeprefix("connector ")
            connectors[current] = []
        elif current is not None and line == f"end {current};":
            current = None
        elif current is not None and line:
            connectors[current].append(line)
    return connectors


def _texts(root: Path) -> dict[str, str]:
    """Every generated file under ``root``, keyed by relative posix path."""
    return {
        path.relative_to(root).as_posix(): path.read_text(encoding="utf-8")
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _generate(subject: str, output_dir: Path, **kwargs: object) -> list[Path]:
    return generate_modelica(
        fixture_path(subject, f"{subject}.sysml"), output_dir, **kwargs
    )


@pytest.mark.parametrize("subject", SUBJECTS)
def test_files_match_the_golden(subject: str, tmp_path: Path) -> None:
    """The committed package is the artifact under test."""
    paths = _generate(subject, tmp_path)

    assert sorted(path.name for path in paths) == sorted(FILES)
    assert {path.parent.name for path in paths} == {"GeneratedInterfaces"}
    for name in FILES:
        assert_golden_text(
            GOLDEN / subject / "GeneratedInterfaces" / name,
            (tmp_path / "GeneratedInterfaces" / name).read_text(encoding="utf-8"),
        )


@pytest.mark.parametrize("subject", SUBJECTS)
def test_generation_is_deterministic(subject: str, tmp_path: Path) -> None:
    """Two runs produce identical bytes; nothing reads a clock or a hash seed."""
    first = _generate(subject, tmp_path / "one")
    second = _generate(subject, tmp_path / "two")
    assert [path.relative_to(tmp_path / "one") for path in first] == [
        path.relative_to(tmp_path / "two") for path in second
    ]
    assert _texts(tmp_path / "one") == _texts(tmp_path / "two")


@pytest.mark.parametrize("subject", SUBJECTS)
def test_no_domain_specific_name_is_emitted(subject: str, tmp_path: Path) -> None:
    """The draft's hard-coded package and model names are gone."""
    _generate(subject, tmp_path / "default")
    _generate(
        subject,
        tmp_path / "custom",
        package="Models",
        within="Enclosing",
    )
    for root in (tmp_path / "default", tmp_path / "custom"):
        for name, text in _texts(root).items():
            for forbidden in FORBIDDEN:
                assert forbidden not in text, f"{forbidden} leaked into {name}"


@pytest.mark.parametrize("subject", SUBJECTS)
def test_within_is_configurable(subject: str, tmp_path: Path) -> None:
    """``within`` reaches the root clause and nests every subpackage."""
    _generate(subject, tmp_path / "default")
    default = _texts(tmp_path / "default")
    assert default["GeneratedInterfaces/package.mo"].splitlines()[0] == "within ;"
    assert default["GeneratedInterfaces/Interfaces.mo"].splitlines()[0] == (
        "within GeneratedInterfaces;"
    )
    assert default["GeneratedInterfaces/GeneratedInterfaces.mo"].splitlines()[0] == (
        "within GeneratedInterfaces;"
    )

    _generate(subject, tmp_path / "named", within="Models.Sub")
    named = _texts(tmp_path / "named")
    assert named["GeneratedInterfaces/package.mo"].splitlines()[0] == (
        "within Models.Sub;"
    )
    assert named["GeneratedInterfaces/Interfaces.mo"].splitlines()[0] == (
        "within Models.Sub.GeneratedInterfaces;"
    )
    assert named[
        "GeneratedInterfaces/GeneratedInterfaces.mo"
    ].splitlines()[0] == "within Models.Sub.GeneratedInterfaces;"
    for name, text in named.items():
        if not name.endswith(".mo"):
            continue
        assert text.splitlines()[0] != default[name].splitlines()[0], name


@pytest.mark.parametrize("subject", SUBJECTS)
def test_package_name_is_configurable(subject: str, tmp_path: Path) -> None:
    """The root package name is an argument, not a constant."""
    paths = _generate(subject, tmp_path, package="Anything")

    assert [path.parent for path in paths] == [tmp_path / "Anything"] * len(paths)
    package = (tmp_path / "Anything" / "package.mo").read_text(encoding="utf-8")
    assert "package Anything" in package
    assert "end Anything;" in package
    for name in ("Interfaces.mo", "GeneratedInterfaces.mo"):
        text = (tmp_path / "Anything" / name).read_text(encoding="utf-8")
        assert text.splitlines()[0] == "within Anything;"


def test_the_package_order_lists_both_subpackages(tmp_path: Path) -> None:
    """Modelica loads subpackages only when the order file names them."""
    _generate("minimal", tmp_path)
    order = (tmp_path / "GeneratedInterfaces" / "package.order").read_text(
        encoding="utf-8"
    )
    assert order == "Interfaces\nGeneratedInterfaces\n"


def test_interfaces_aliases_all_four_primitives(tmp_path: Path) -> None:
    """Every FMI primitive has an input and an output connector alias."""
    _generate("minimal", tmp_path)
    text = (tmp_path / "GeneratedInterfaces" / "Interfaces.mo").read_text(
        encoding="utf-8"
    )
    assert text.splitlines() == [
        "within GeneratedInterfaces;",
        "package Interfaces",
        "  connector RealInput = input Real;",
        "  connector RealOutput = output Real;",
        "  connector IntegerInput = input Integer;",
        "  connector IntegerOutput = output Integer;",
        "  connector BooleanInput = input Boolean;",
        "  connector BooleanOutput = output Boolean;",
        "  connector StringInput = input String;",
        "  connector StringOutput = output String;",
        "end Interfaces;",
    ]


@pytest.mark.parametrize("subject", SUBJECTS)
def test_connector_members_follow_the_port_direction(
    subject: str, tmp_path: Path
) -> None:
    """Integer and Boolean fields carry the direction; inout stays undirected."""
    _generate(subject, tmp_path)
    connectors = _connectors(
        tmp_path / "GeneratedInterfaces" / "GeneratedInterfaces.mo"
    )
    assert connectors == CONNECTORS[subject]


def test_inout_and_mixed_directions_stay_undirected(tmp_path: Path) -> None:
    """A connector used both ways declares no direction at all."""
    _generate("bus", tmp_path)
    connectors = _connectors(
        tmp_path / "GeneratedInterfaces" / "GeneratedInterfaces.mo"
    )
    # ``Orientation`` is used ``in``, ``out``, and ``inout``; ``Position`` both
    # ``in`` and ``out``. Neither may claim one direction for all its users.
    for name in ("Orientation", "Position"):
        for member in connectors[name]:
            assert not member.startswith(("input ", "output ")), member


def test_string_and_array_fields_reach_the_connector(tmp_path: Path) -> None:
    """A String field and a fixed-length array keep their type and shape."""
    architecture = tmp_path / "probe.sysml"
    architecture.write_text(
        """package Probe {
  port def ParameterInterface;

  port def Text {
    attribute label : String;
    attribute samples : Real[3];
  }

  part def Device {
    in port text : Text;
  }

  part def Root {
    part device : Device;
  }
}
""",
        encoding="utf-8",
    )

    generate_modelica(architecture, tmp_path / "out")
    connectors = _connectors(
        tmp_path / "out" / "GeneratedInterfaces" / "GeneratedInterfaces.mo"
    )
    assert connectors == {"Text": ["input String label;", "input Real samples[3];"]}


@pytest.mark.skipif(
    shutil.which("omc") is None or not OMC.is_file(),
    reason="omc is not installed",
)
@pytest.mark.slow
def test_openmodelica_accepts_the_generated_packages(tmp_path: Path) -> None:
    """The only syntactic oracle: the Modelica toolchain parses and checks it."""
    packages: list[Path] = []
    for subject in SUBJECTS:
        _generate(subject, tmp_path / subject)
        packages.append(
            tmp_path / subject / "GeneratedInterfaces" / "package.mo"
        )

    mos = tmp_path / "check.mos"
    lines = [
        f'loadFile("{path.as_posix()}");' for path in packages
    ]
    for _ in packages:
        lines.append("checkModel(GeneratedInterfaces.GeneratedInterfaces);")
        lines.append("checkModel(GeneratedInterfaces.Interfaces);")
    lines.append("getErrorString();")
    mos.write_text("\n".join(lines) + "\n", encoding="utf-8")

    result = subprocess.run(
        [str(OMC), str(mos)], capture_output=True, text=True, check=False
    )

    assert result.returncode == 0, result.stdout + result.stderr
    combined = result.stdout + result.stderr
    assert "Error" not in combined, combined
    assert combined.count("completed successfully") == 2 * len(packages)
