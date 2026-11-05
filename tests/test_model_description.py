"""Component tests for ``modelDescription.xml`` generation.

The generator is run against the architecture fixtures into a temporary
directory; the tests then read the files back with the independent
``pyssp_standard`` codec and validator. The goldens pin the bytes, the
assertions pin the contract.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from pathlib import Path

import pycps_sysml2
import pytest
from pyssp_standard.standard.fmi2.codec import Fmi2ModelDescriptionXmlCodec
from pyssp_standard.standard.fmi2.validation import Fmi2ModelDescriptionValidator

from conftest import GENERATION_TIME, GOLDEN_ROOT, fixture_path
from golden_utils import assert_golden_text
from pyfmi_sysml2.interface import components
from pyfmi_sysml2.model_description import (
    component_guid,
    generate_model_description,
    model_description_document,
    render_model_description,
)

pytestmark = pytest.mark.component

CODEC = Fmi2ModelDescriptionXmlCodec()

#: Fixture subjects; each has exactly one leaf component.
SUBJECTS = ("minimal", "sensor", "controller", "bus")

#: ``component_guid("ControllerComposition", "Controller")``, computed by the
#: test from ``uuid5(NAMESPACE_URL, "pyssp_sysml2/<composition>/<component>")``.
CONTROLLER_GUID = "{64044cfb-9f40-5998-99f1-6652e4828def}"

CASE_HEADINGS = (
    "# Case:",
    "## Artifacts",
    "## What this case proves",
    "## Update history",
)

CASE_FIELDS = (
    "**Conversion:**",
    "**Requirement / fault:**",
    "**Level:**",
    "**Input:**",
    "**Expected:**",
    "**Independent oracle:**",
    "**Comparison:**",
    "**Normalization:**",
    "**Volatile fields:**",
    "**Update policy:**",
    "**Notes:**",
)

#: Two leaf components, declared out of name order.
PAIR_MODEL = """package Pair {
  port def Signal {
    attribute value : Real;
  }

  part def Zulu {
    in port u : Signal;
    out port y : Signal;
  }

  part def Alpha {
    in port u : Signal;
    out port y : Signal;
  }

  part def PairComposition {
    part zulu : Zulu;
    part alpha : Alpha;
  }
}
"""

#: A typed parameter port: a Boolean and an Integer default besides a Real.
TYPED_MODEL = """package Typed {
  port def ParameterInterface;
  attribute def ParameterSet;

  port def Signal {
    attribute value : Real;
  }

  port def FlagParameters :> ParameterInterface {
    attribute enabled : Boolean = true;
    attribute count : Integer = 3;
  }

  part def Flagged {
    doc /* A component with a typed parameter port. */
    in port parameters : FlagParameters;
    in port u : Signal;
    out port y : Signal;
  }

  part def TypedComposition {
    part flagged : Flagged;
  }
}
"""

#: The interface default must win over the parameter set applied by ``bind``;
#: the composition also carries its default experiment as control attributes.
APPLIED_SET_MODEL = """package Applied {
  port def ParameterInterface;
  attribute def ParameterSet;

  port def Signal {
    attribute value : Real;
  }

  port def GainParameters :> ParameterInterface {
    attribute gains : Real[2] = (1.0, 2.5);
  }

  attribute def TunedSet :> ParameterSet {
    attribute gains : Real[2] = (9.0, 9.5);
  }

  part def Scale {
    in port parameters : GainParameters;
    in port u : Signal;
    out port y : Signal;
  }

  part def AppliedComposition {
    part scale : Scale;
    attribute tuned : TunedSet;
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 10.0;
    bind scale.parameters = tuned;
  }
}
"""


def _write_model(directory: Path, text: str) -> Path:
    path = directory / "model.sysml"
    path.write_text(text, encoding="utf-8")
    return path


def _generate(subject: str, output_dir: Path, **kwargs) -> list[Path]:
    return generate_model_description(
        fixture_path(subject, f"{subject}.sysml"),
        output_dir,
        generation_time=GENERATION_TIME,
        **kwargs,
    )


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@pytest.mark.parametrize("subject", SUBJECTS)
def test_every_generated_file_validates(subject: str, tmp_path: Path) -> None:
    """Each written file re-parses and passes the independent validator."""
    written = _generate(subject, tmp_path)

    assert written
    for path in written:
        xml = _read(path)
        Fmi2ModelDescriptionValidator().validate(CODEC.parse(xml), xml)


def test_same_generation_time_is_byte_identical(tmp_path: Path) -> None:
    first = _generate("sensor", tmp_path / "first")
    second = _generate("sensor", tmp_path / "second")

    assert [path.read_bytes() for path in first] == [
        path.read_bytes() for path in second
    ]


def test_another_generation_time_changes_only_the_timestamp(
    tmp_path: Path,
) -> None:
    earlier = _read(_generate("sensor", tmp_path / "earlier")[0])
    later = _read(
        generate_model_description(
            fixture_path("sensor", "sensor.sysml"),
            tmp_path / "later",
            generation_time=GENERATION_TIME + timedelta(hours=1),
        )[0]
    )

    assert 'generationDateAndTime="2026-01-01T01:00:00Z"' in later
    assert later.replace("2026-01-01T01:00:00Z", "@") == earlier.replace(
        "2026-01-01T00:00:00Z", "@"
    )


def test_controller_guid_is_pinned(tmp_path: Path) -> None:
    """``guid`` is ``uuid5(NAMESPACE_URL, "pyssp_sysml2/<composition>/<name>")``.

    Computed here from the frozen namespace string, so a namespace, input, or
    formatting change fails instead of silently regenerating every guid.
    """
    expected = (
        "{"
        + str(
            uuid.uuid5(
                uuid.NAMESPACE_URL,
                "pyssp_sysml2/ControllerComposition/Controller",
            )
        )
        + "}"
    )

    [path] = _generate("controller", tmp_path)

    assert CODEC.parse(_read(path)).guid == expected
    assert component_guid("ControllerComposition", "Controller") == expected
    assert expected == CONTROLLER_GUID


def test_controller_variable_summary_is_exact() -> None:
    """Names, value references, causalities, variabilities, starts, and types."""
    architecture = pycps_sysml2.load(
        fixture_path("controller", "controller.sysml")
    )

    document = model_description_document(
        architecture,
        "Controller",
        generation_time=GENERATION_TIME,
    )

    assert [
        (
            variable.name,
            variable.value_reference,
            variable.causality,
            variable.variability,
            variable.start,
            variable.type_name,
        )
        for variable in document.variables
    ] == [
        ("gains[0]", 0, "parameter", "fixed", "1", "Real"),
        ("gains[1]", 1, "parameter", "fixed", "2.5", "Real"),
        ("label", 2, "parameter", "fixed", "nominal", "String"),
        ("command.manual", 3, "input", None, None, "Real"),
        ("command.auto", 4, "input", None, None, "Real"),
        ("command.mode", 5, "input", None, None, "Integer"),
        ("throttle.demand", 6, "output", None, None, "Real"),
        ("throttle.enabled", 7, "output", None, None, "Boolean"),
        ("status.code", 8, "output", None, None, "Integer"),
    ]
    assert [
        unknown.index for unknown in document.model_structure.outputs
    ] == [7, 8, 9]
    assert [
        unknown.index for unknown in document.model_structure.initial_unknowns
    ] == [7, 8, 9]


def test_boolean_start_is_fmi_text(tmp_path: Path) -> None:
    """``Boolean`` starts are ``true``/``false``, never ``str(True)``."""
    [path] = generate_model_description(
        _write_model(tmp_path, TYPED_MODEL),
        tmp_path / "out",
        generation_time=GENERATION_TIME,
    )

    document = CODEC.parse(_read(path))

    assert [(variable.name, variable.start) for variable in document.parameters] == [
        ("enabled", "true"),
        ("count", 3),
    ]
    assert '<Boolean start="true" />' in _read(path)
    assert "True" not in _read(path)


def test_interface_default_wins_over_an_applied_parameter_set(
    tmp_path: Path,
) -> None:
    """The reduction reads parameter defaults from the interface only."""
    [path] = generate_model_description(
        _write_model(tmp_path, APPLIED_SET_MODEL),
        tmp_path / "out",
        generation_time=GENERATION_TIME,
    )

    document = CODEC.parse(_read(path))

    assert [(variable.name, variable.start) for variable in document.parameters] == [
        ("gains[0]", 1.0),
        ("gains[1]", 2.5),
    ]


def test_default_experiment_comes_from_composition_control_attributes(
    tmp_path: Path,
) -> None:
    [path] = generate_model_description(
        _write_model(tmp_path, APPLIED_SET_MODEL),
        tmp_path / "out",
        generation_time=GENERATION_TIME,
    )

    experiment = CODEC.parse(_read(path)).default_experiment

    assert experiment is not None
    assert experiment.start_time == 0.0
    assert experiment.stop_time == 10.0


def test_no_default_experiment_without_control_attributes(tmp_path: Path) -> None:
    [path] = _generate("minimal", tmp_path)

    assert CODEC.parse(_read(path)).default_experiment is None


def test_naive_generation_time_is_refused(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        generate_model_description(
            fixture_path("minimal", "minimal.sysml"),
            tmp_path,
            generation_time=datetime(2026, 1, 1),
        )


def test_output_layout_is_sorted_by_component_name(tmp_path: Path) -> None:
    written = generate_model_description(
        _write_model(tmp_path, PAIR_MODEL),
        tmp_path / "out",
        generation_time=GENERATION_TIME,
    )

    assert [
        path.relative_to(tmp_path / "out").as_posix() for path in written
    ] == ["Alpha/modelDescription.xml", "Zulu/modelDescription.xml"]


def test_component_filter_selects_one_and_refuses_an_unknown(tmp_path: Path) -> None:
    written = _generate("controller", tmp_path / "selected", component="Controller")

    assert [
        path.relative_to(tmp_path / "selected").as_posix() for path in written
    ] == ["Controller/modelDescription.xml"]

    with pytest.raises(ValueError, match="No exported component named 'Missing'"):
        _generate("controller", tmp_path / "missing", component="Missing")


def test_document_round_trips_through_the_codec(tmp_path: Path) -> None:
    architecture = pycps_sysml2.load(_write_model(tmp_path, APPLIED_SET_MODEL))
    component = components(architecture)[0]

    document = model_description_document(
        architecture,
        component,
        generation_time=GENERATION_TIME,
    )
    parsed = CODEC.parse(
        render_model_description(
            architecture,
            component,
            generation_time=GENERATION_TIME,
        )
    )

    assert parsed.fmi_version == document.fmi_version == "2.0"
    assert parsed.model_name == document.model_name
    assert parsed.guid == document.guid
    assert parsed.description == document.description
    assert parsed.generation_tool == document.generation_tool
    assert parsed.generation_date_and_time == document.generation_date_and_time
    assert parsed.variable_naming_convention == document.variable_naming_convention
    assert parsed.interface_type == document.interface_type == "CoSimulation"
    assert parsed.capabilities is not None
    assert parsed.capabilities.model_identifier == "Scale"
    assert [
        (
            variable.name,
            variable.value_reference,
            variable.type_name,
            variable.causality,
            variable.variability,
        )
        for variable in parsed.variables
    ] == [
        ("gains[0]", 0, "Real", "parameter", "fixed"),
        ("gains[1]", 1, "Real", "parameter", "fixed"),
        ("u.value", 2, "Real", "input", None),
        ("y.value", 3, "Real", "output", None),
    ]
    assert [variable.start for variable in parsed.parameters] == [1.0, 2.5]
    assert [
        unknown.index for unknown in parsed.model_structure.outputs
    ] == [4]
    assert [
        unknown.index for unknown in parsed.model_structure.initial_unknowns
    ] == [4]
    assert parsed.default_experiment == document.default_experiment


@pytest.mark.parametrize("subject", SUBJECTS)
def test_golden_model_description(subject: str, tmp_path: Path) -> None:
    """Generated bytes equal the committed golden for every fixture."""
    written = _generate(subject, tmp_path)

    assert len(written) == 1
    [path] = written
    assert path.parent.parent == tmp_path

    golden = (
        GOLDEN_ROOT
        / "model-description"
        / subject
        / path.parent.name
        / path.name
    )
    assert_golden_text(golden, _read(path))


@pytest.mark.parametrize("subject", SUBJECTS)
def test_case_record_is_complete(subject: str) -> None:
    """Every subject carries a provenance record with the required fields."""
    text = _read(GOLDEN_ROOT / "model-description" / subject / "case.md")

    for marker in CASE_HEADINGS + CASE_FIELDS:
        assert marker in text, f"{subject}/case.md lacks {marker!r}"
