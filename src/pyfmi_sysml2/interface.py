"""Reduction of a SysML architecture onto the FMI interface it must expose.

Every generator in this package reads the architecture through this module, so
that the modelDescription, the C headers, and the Modelica connectors cannot
disagree about *which* variables exist. The reduction follows the
``pyssp_sysml2`` v0.3.0 FMI policy:

- parameters come from the parameter dialect only (``in port parameters ...``),
  never from flat part attributes, and keep their interface defaults;
- a parameter list is expanded into one scalar per element, named
  ``<name>[<index>]``, zero-based;
- port fields are named ``<port>.<field>`` and expanded the same way;
- value references restart at 0 for every component, parameters first, then
  ports in declaration order and fields in declaration order.

FMI 2.0 has no array variable and no bidirectional scalar, so an ``inout`` or
undirected port becomes an input and the Modelica connector keeps the
direction out of the signal declaration.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from pycps_sysml2 import Architecture, Attribute, PartDefinition
from pycps_sysml2.core import (
    CONTROL,
    FLAT_CONNECTOR_ATTR,
    format_value,
    map_fmi_type,
)
from pycps_sysml2.parameters import (
    SSP_POLICY,
    component_definitions,
    is_parameter_interface,
    parameter_declarations,
    parameter_items,
    validate_parameter_dialect,
)

#: FMI primitive name to C type used by the generated headers.
C_TYPES = {
    "Real": "double",
    "Integer": "int",
    "Boolean": "bool",
    "String": "const char*",
}

#: FMI primitive name to the C++ member type used inside ``*_Instance``.
CPP_TYPES = {
    "Real": "double",
    "Integer": "int",
    "Boolean": "bool",
    "String": "std::string",
}

#: FMI primitive name to the generated ``*_DataType`` enumerator suffix.
DATA_TYPE_TAGS = {
    "Real": "REAL",
    "Integer": "INTEGER",
    "Boolean": "BOOLEAN",
    "String": "STRING",
}

#: FMI primitive name to the Modelica type used in connectors.
MODELICA_TYPES = {
    "Real": "Real",
    "Integer": "Integer",
    "Boolean": "Boolean",
    "String": "String",
}

_INDEXED = re.compile(r"^(?P<base>.+)\[(?P<index>\d+)\]$")


def c_type(type_name: str, *, cpp: bool = False) -> str:
    """C or C++ storage type for an FMI primitive."""
    table = CPP_TYPES if cpp else C_TYPES
    return table.get(type_name, table["Real"])


def modelica_type(type_name: str) -> str:
    """Modelica type for an FMI primitive (unknown types keep their name)."""
    return MODELICA_TYPES.get(type_name, type_name)


def sanitize_identifier(text: str) -> str:
    """Upper-case a dotted or bracketed name into a C identifier fragment."""
    return re.sub(r"[^0-9A-Za-z]", "_", text).upper()


def direction_causality(direction: str | None) -> str:
    """FMI causality for a SysML port direction.

    FMI 2.0 CoSimulation has no bidirectional scalar variable, so ``inout`` and
    an undirected port are exposed as inputs.
    """
    return "output" if direction == "out" else "input"


@dataclass(frozen=True)
class Field:
    """One declared member: a scalar, or a fixed-length array."""

    name: str
    type_name: str
    array: int | None = None

    def members(self) -> list[tuple[str, str]]:
        """``(fmi_suffix, member_expression)`` for every element."""
        if self.array is None:
            return [("", self.name)]
        return [(f"[{i}]", f"{self.name}[{i}]") for i in range(self.array)]


@dataclass(frozen=True)
class Variable:
    """One FMI ScalarVariable, with its C member expression."""

    name: str
    type_name: str
    causality: str
    variability: str | None
    value_reference: int
    index: int
    description: str | None
    start: object | None
    member: str

    @property
    def start_text(self) -> str | None:
        """XML text for ``start``, or ``None`` when no default was authored."""
        if self.start is None:
            return None
        return format_value(self.type_name, self.start)

    @property
    def writable(self) -> bool:
        """Whether the C mapping may write through this value reference."""
        return self.causality != "output"


@dataclass(frozen=True)
class PortGroup:
    """A port usage: its payload fields and their FMI variables."""

    name: str
    definition: str
    direction: str | None
    causality: str
    fields: tuple[Field, ...]
    doc: str | None

    @property
    def modelica_qualifier(self) -> str:
        """Modelica declaration prefix for the connector field."""
        if self.direction == "in":
            return "input "
        if self.direction == "out":
            return "output "
        return ""


@dataclass(frozen=True)
class Component:
    """A leaf part definition and its complete FMI interface."""

    name: str
    doc: str | None
    parameters: tuple[Field, ...]
    ports: tuple[PortGroup, ...]
    variables: tuple[Variable, ...]

    @property
    def outputs(self) -> tuple[Variable, ...]:
        return tuple(v for v in self.variables if v.causality == "output")

    @property
    def vr_count(self) -> int:
        return len(self.variables)


def _fixed_count(multiplicity: str | None, value: object) -> int | None:
    """Declared element count for a field, or ``None`` for a scalar."""
    if multiplicity:
        text = multiplicity
        if ".." in text:
            lower, upper = text.split("..", 1)
            if lower != upper:
                raise ValueError(
                    f"Variable multiplicity '[{text}]' is not a fixed length; "
                    "FMI 2.0 needs one scalar per element"
                )
            text = lower
        try:
            return int(text)
        except ValueError:
            raise ValueError(
                f"Unsupported multiplicity '[{multiplicity}]'"
            ) from None
    if isinstance(value, tuple):
        return len(value)
    return None


def _field_dtype(attribute: Attribute) -> str:
    return map_fmi_type(attribute.primitive_type_str())


def _is_signal_port(architecture: Architecture, part_def: PartDefinition) -> bool:
    """True for a port that carries FMI signal fields, not parameters."""
    if part_def is None:
        return False
    return not is_parameter_interface(part_def)


def component_interface(
    architecture: Architecture, part_def: PartDefinition
) -> Component:
    """Build the FMI interface of one leaf part definition."""
    parameters: list[Field] = []
    variables: list[Variable] = []
    counter = 0

    for attribute in parameter_declarations(architecture, part_def):
        type_name = _field_dtype(attribute)
        items = parameter_items(attribute)
        count = len(items)
        array = count if count > 1 or attribute.multiplicity else None
        parameters.append(Field(attribute.name, type_name, array))
        for item in items:
            counter += 1
            variables.append(
                Variable(
                    name=item.name,
                    type_name=type_name,
                    causality="parameter",
                    variability="fixed",
                    value_reference=counter - 1,
                    index=counter,
                    description=attribute.doc,
                    start=item.value,
                    member=item.name,
                )
            )

    ports: list[PortGroup] = []
    for name, usage in part_def.ports.items():
        if CONTROL.is_control(name):
            continue
        definition = architecture.resolve_port(usage)
        if definition is None:
            raise ValueError(
                f"Unresolved port definition for {part_def.name}.{name}"
            )
        if not _is_signal_port(architecture, definition):
            continue
        flat = definition.attributes.get(FLAT_CONNECTOR_ATTR)
        if flat is not None and bool(flat.value):
            # v0.1.0 does not flatten connector payloads into the component;
            # record rather than silently change the variable set.
            raise ValueError(
                f"{part_def.name}.{name} sets {FLAT_CONNECTOR_ATTR}; flattened "
                "ports are not supported by pyfmi_sysml2 v0.1.0"
            )
        causality = direction_causality(usage.direction)
        fields: list[Field] = []
        for attribute in definition.attributes.values():
            if CONTROL.is_control(attribute.name):
                continue
            type_name = _field_dtype(attribute)
            array = _fixed_count(attribute.multiplicity, attribute.value)
            fields.append(Field(attribute.name, type_name, array))
            for suffix, member in fields[-1].members():
                counter += 1
                variables.append(
                    Variable(
                        name=f"{name}.{attribute.name}{suffix}",
                        type_name=type_name,
                        causality=causality,
                        variability=None,
                        value_reference=counter - 1,
                        index=counter,
                        description=(
                            attribute.doc or usage.doc or definition.doc
                        ),
                        start=None,
                        member=f"{name}.{member}",
                    )
                )
        ports.append(
            PortGroup(
                name=name,
                definition=definition.name,
                direction=usage.direction,
                causality=causality,
                fields=tuple(fields),
                doc=usage.doc or definition.doc,
            )
        )

    return Component(
        name=part_def.name,
        doc=part_def.doc,
        parameters=tuple(parameters),
        ports=tuple(ports),
        variables=tuple(variables),
    )


def resolve_system(
    architecture: Architecture, composition: str | None = None
) -> PartDefinition:
    """The part definition whose components are exported.

    ``composition`` names it explicitly. Without a name, the single part
    definition that has parts and is not used as a part elsewhere is taken;
    an architecture with several such roots must name one.
    """
    if composition is not None:
        return architecture.get_part_def(composition)

    used: set[str] = set()
    for definition in architecture.part_definitions.values():
        for usage in definition.parts.values():
            resolved = architecture.resolve_part(usage)
            if resolved is not None:
                used.add(resolved.name)
    roots = [
        definition
        for name, definition in architecture.part_definitions.items()
        if definition.parts and name not in used
    ]
    if len(roots) != 1:
        names = ", ".join(sorted(definition.name for definition in roots))
        raise ValueError(
            "Cannot pick a composition root; "
            f"{len(roots)} candidates ({names or 'none'}). Pass composition=."
        )
    return roots[0]


def components(
    architecture: Architecture,
    *,
    composition: str | None = None,
) -> list[Component]:
    """Every exported leaf component, sorted by name.

    The parameter dialect is validated first, so a flat parameter attribute is
    reported instead of silently dropped.
    """
    system = resolve_system(architecture, composition)
    validate_parameter_dialect(architecture, system, policy=SSP_POLICY)
    return [
        component_interface(architecture, definition)
        for definition in sorted(
            component_definitions(architecture, system),
            key=lambda candidate: candidate.name,
        )
        if not definition.parts
    ]


def component(
    architecture: Architecture,
    name: str,
    *,
    composition: str | None = None,
) -> Component:
    """One named leaf component."""
    for candidate in components(architecture, composition=composition):
        if candidate.name == name:
            return candidate
    raise KeyError(f"No exported component named {name!r}")
