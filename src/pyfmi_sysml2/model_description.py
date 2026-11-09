"""FMI 2.0 CoSimulation ``modelDescription.xml`` generation.

The variable set, the causalities, and the start values come from
:mod:`pyfmi_sysml2.interface`; this module only maps that reduction onto the
``pyssp_standard`` FMI 2 document model and serializes it. The document is
validated before it reaches disk, so a file this module writes is one the
library's own XSD and semantic validators accept.

Identity is frozen for cross-library reproducibility: the ``guid`` and the
``modelName`` of a component must match pyssp_sysml2 v0.3.0, because the two
generators write into the same model directories during migration.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path

import pycps_sysml2
from pycps_sysml2 import Architecture, PartDefinition
from pycps_sysml2.core import CONTROL
from pyssp_standard.standard.fmi2.codec import Fmi2ModelDescriptionXmlCodec
from pyssp_standard.standard.fmi2.model import (
    Fmi2DefaultExperiment,
    Fmi2ElementInfo,
    Fmi2InterfaceAttributes,
    Fmi2ModelDescriptionDocument,
    Fmi2ModelStructure,
    Fmi2ScalarVariable,
    Fmi2Unknown,
)
from pyssp_standard.standard.fmi2.validation import Fmi2ModelDescriptionValidator

from pyfmi_sysml2.interface import (
    Component,
    ExportIdentity,
    components,
    export_identity,
    resolve_system,
)

#: FMI version emitted for every generated document.
FMI_VERSION = "2.0"

#: ``generationTool`` stamped into every document.
GENERATION_TOOL = "pyfmi_sysml2 tooling"

#: FMI ``dateTime`` form: UTC, second precision.
GENERATION_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

#: Namespace the FMI ``guid`` is derived from.
GUID_NAMESPACE = uuid.NAMESPACE_URL


def utc_now() -> datetime:
    """Current time in UTC; the clock hook for ``generationDateAndTime``."""
    return datetime.now(timezone.utc)


def format_generation_time(moment: datetime | None) -> str:
    """Render a timezone-aware time as an FMI ``dateTime``.

    ``None`` means now. A naive time is rejected rather than guessed at, because
    the artifact would then depend on the host's locality.
    """
    if moment is None:
        moment = utc_now()
    if moment.tzinfo is None or moment.utcoffset() is None:
        raise ValueError(
            "generation_time must be timezone-aware, e.g. "
            "datetime(2026, 1, 1, tzinfo=timezone.utc)"
        )
    return moment.astimezone(timezone.utc).strftime(GENERATION_TIME_FORMAT)


def _guid(key: str) -> str:
    """Format one uuid5 namespace key as an FMI ``guid``."""
    return "{" + str(uuid.uuid5(GUID_NAMESPACE, key)) + "}"


def component_guid(composition: str, component: str) -> str:
    """Stable FMI ``guid`` for one component of one container composition.

    The namespace string is frozen verbatim from pyssp_sysml2 v0.3.0
    (``artifacts/fmi.py:183-185``): the ``pyssp_sysml2/`` prefix stays even
    though this package is named differently, so migrating a build from one
    generator to the other does not change a single guid. A direct FMU model
    has no container level; :class:`ExportIdentity` derives that form.
    """
    return _guid(ExportIdentity(composition, False).guid_key(component))


def _control_float(system: PartDefinition, name: str) -> float | None:
    """The literal ``Real`` value of one control attribute, when present."""
    attribute = system.attributes.get(name)
    if attribute is None:
        return None
    if attribute.value is None:
        raise ValueError(f"{system.name}.{name} needs a Real literal value")
    return float(attribute.value)


def default_experiment(system: PartDefinition) -> Fmi2DefaultExperiment | None:
    """The composition's ``DefaultExperiment``, or ``None`` when unset."""
    start = _control_float(system, CONTROL.default_start)
    stop = _control_float(system, CONTROL.default_stop)
    if start is None and stop is None:
        return None
    return Fmi2DefaultExperiment(start_time=start, stop_time=stop)


def _select_component(
    architecture: Architecture,
    name: str,
    *,
    composition: str | None,
    base_index: int = 0,
) -> Component:
    for candidate in components(
        architecture, composition=composition, base_index=base_index
    ):
        if candidate.name == name:
            return candidate
    raise ValueError(f"No exported component named {name!r}")


def model_description_document(
    architecture: Architecture,
    component: Component | str,
    *,
    composition: str | None = None,
    generation_time: datetime | None = None,
    base_index: int = 0,
) -> Fmi2ModelDescriptionDocument:
    """The FMI 2.0 document for one component, before serialization.

    ``base_index`` selects the ``[i]`` suffix base of array variable names
    (default 0; 1 targets OMC-built Modelica FMUs).
    """
    if isinstance(component, str):
        component = _select_component(
            architecture, component, composition=composition, base_index=base_index
        )
    system = resolve_system(architecture, composition)
    identity = export_identity(architecture, system)

    outputs = [Fmi2Unknown(index=variable.index) for variable in component.outputs]
    return Fmi2ModelDescriptionDocument(
        root=Fmi2ElementInfo(tag="fmiModelDescription"),
        fmi_version=FMI_VERSION,
        model_name=identity.model_name(component.name),
        guid=_guid(identity.guid_key(component.name)),
        description=component.doc or None,
        generation_tool=GENERATION_TOOL,
        generation_date_and_time=format_generation_time(generation_time),
        variable_naming_convention="structured",
        # Both fields are required: the codec emits the interface element only
        # when it has an interface type *and* its attributes.
        interface_type="CoSimulation",
        capabilities=Fmi2InterfaceAttributes(model_identifier=component.name),
        variables=[
            Fmi2ScalarVariable(
                name=variable.name,
                value_reference=variable.value_reference,
                type_name=variable.type_name,
                description=variable.description,
                causality=variable.causality,
                variability=variable.variability,
                start=variable.start_text,
            )
            for variable in component.variables
        ],
        model_structure=Fmi2ModelStructure(
            outputs=outputs,
            initial_unknowns=[
                Fmi2Unknown(index=variable.index) for variable in component.outputs
            ],
        ),
        default_experiment=default_experiment(system),
    )


def render_model_description(
    architecture: Architecture,
    component: Component | str,
    *,
    composition: str | None = None,
    generation_time: datetime | None = None,
    base_index: int = 0,
) -> str:
    """Serialize and validate one component's model description."""
    document = model_description_document(
        architecture,
        component,
        composition=composition,
        generation_time=generation_time,
        base_index=base_index,
    )
    xml = Fmi2ModelDescriptionXmlCodec().serialize(document)
    Fmi2ModelDescriptionValidator().validate(document, xml)
    return xml


def generate_model_description(
    source: Path | str | Architecture,
    output_dir: Path | str,
    *,
    composition: str | None = None,
    component: str | None = None,
    generation_time: datetime | None = None,
    base_index: int = 0,
) -> list[Path]:
    """Write ``<output_dir>/<Component>/modelDescription.xml`` per leaf.

    ``source`` is an architecture or the path of one (file or directory).
    ``component`` narrows the run to one component and fails when it is not
    exported. ``generation_time`` fixes ``generationDateAndTime``; ``None``
    stamps the current UTC time, a naive time is refused. ``base_index``
    selects the ``[i]`` suffix base of array variable names (default 0; 1
    targets OMC-built Modelica FMUs).
    """
    architecture = (
        source
        if isinstance(source, Architecture)
        else pycps_sysml2.load(source)
    )
    if generation_time is not None:
        format_generation_time(generation_time)

    selected = components(
        architecture, composition=composition, base_index=base_index
    )
    if component is not None:
        selected = [
            candidate for candidate in selected if candidate.name == component
        ]
        if not selected:
            raise ValueError(f"No exported component named {component!r}")

    root = Path(output_dir)
    written: list[Path] = []
    for candidate in selected:
        document = model_description_document(
            architecture,
            candidate,
            composition=composition,
            generation_time=generation_time,
        )
        xml = Fmi2ModelDescriptionXmlCodec().serialize(document)
        Fmi2ModelDescriptionValidator().validate(document, xml)

        path = root / candidate.name / "modelDescription.xml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(xml, encoding="utf-8")
        written.append(path)
    return written
