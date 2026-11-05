"""Modelica interface packages generated from a SysML architecture.

The connector set is the sysml-side mirror of the FMI interface: one ``connector``
per distinct port definition used by the exported components, with the same
fields in the same order the FMI reduction uses. The names are configuration,
not constants: the root package, the enclosing ``within`` clause, and the
subpackage layout are arguments, and nothing domain-specific is emitted.

A connector is a type, so a definition used by components in different
directions cannot declare a direction that is true everywhere. The member prefix
is the port direction when every usage agrees on it, and empty when the usages
disagree or any of them is ``inout`` or undirected; a bidirectional connector
has to stay undirected for the Modelica tool to accept it on both sides.

The subpackages are declared inside their parent, so their ``within`` clause is
the root package, nested under ``within`` when one is given; only the root
``package.mo`` carries the bare ``within`` clause.
"""

from __future__ import annotations

from pathlib import Path

from pycps_sysml2 import Architecture, load

from pyfmi_sysml2.interface import Component, Field, components, modelica_type

#: Root package default. The generated files never embed a concrete model name.
DEFAULT_PACKAGE = "GeneratedInterfaces"

#: The primitive connector aliases every generated package carries.
PRIMITIVES = ("Real", "Integer", "Boolean", "String")

#: Subpackage names, also the ``package.order`` entries.
INTERFACES = "Interfaces"
GENERATED = "GeneratedInterfaces"

INDENT = "  "


def _architecture(source: Architecture | str | Path) -> Architecture:
    """The parsed architecture, loading a path on demand."""
    if isinstance(source, Architecture):
        return source
    return load(Path(source))


def _port_definitions(
    exported: list[Component],
) -> dict[str, tuple[tuple[str, str], ...]]:
    """Field sets and member prefix per distinct port definition.

    Keyed by the definition name, sorted. Two usages of one definition must
    agree on the fields; a definition that is used in one direction only keeps
    that direction, anything else stays undirected.
    """
    fields_by_definition: dict[str, tuple[Field, ...]] = {}
    qualifiers: dict[str, set[str]] = {}
    for component in exported:
        for port in component.ports:
            known = fields_by_definition.get(port.definition)
            assert known is None or known == port.fields, (
                f"port definition {port.definition} disagrees between usages: "
                f"{known} != {port.fields}"
            )
            fields_by_definition[port.definition] = port.fields
            qualifiers.setdefault(port.definition, set()).add(
                port.modelica_qualifier
            )

    result: dict[str, tuple[tuple[str, str], ...]] = {}
    for definition in sorted(fields_by_definition):
        prefixes = qualifiers[definition]
        qualifier = next(iter(prefixes)) if len(prefixes) == 1 else ""
        result[definition] = tuple(
            (qualifier, _field_text(field))
            for field in fields_by_definition[definition]
        )
    return result


def _field_text(field: Field) -> str:
    """One connector member without its indent and terminator."""
    type_name = modelica_type(field.type_name)
    if field.array is None:
        return f"{type_name} {field.name}"
    return f"{type_name} {field.name}[{field.array}]"


def _package_text(package: str, within: str | None) -> str:
    header = f"within {within};" if within is not None else "within ;"
    return "\n".join(
        [
            header,
            f"package {package}",
            f'{INDENT}annotation(uses(Modelica(version="4.0.0")));',
            f"end {package};",
            "",
        ]
    )


def _order_text() -> str:
    return f"{INTERFACES}\n{GENERATED}\n"


def _parent_scope(package: str, within: str | None) -> str:
    """Fully qualified name of the root package, as a subpackage sees it."""
    return package if within is None else f"{within}.{package}"


def _interfaces_text(parent: str) -> str:
    lines = [f"within {parent};", f"package {INTERFACES}"]
    for type_name in PRIMITIVES:
        lines.append(
            f"{INDENT}connector {type_name}Input = input {type_name};"
        )
        lines.append(
            f"{INDENT}connector {type_name}Output = output {type_name};"
        )
    lines.append(f"end {INTERFACES};")
    return "\n".join(lines) + "\n"


def _generated_text(
    parent: str, definitions: dict[str, tuple[tuple[str, str], ...]]
) -> str:
    lines = [f"within {parent};", f"package {GENERATED}"]
    for name in sorted(definitions):
        lines.append(f"{INDENT}connector {name}")
        for qualifier, member in definitions[name]:
            lines.append(f"{INDENT * 2}{qualifier}{member};")
        lines.append(f"{INDENT}end {name};")
        lines.append("")
    lines.append(f"end {GENERATED};")
    return "\n".join(lines) + "\n"


def generate_modelica(
    source: Architecture | str | Path,
    output_dir: str | Path,
    *,
    package: str = DEFAULT_PACKAGE,
    within: str | None = None,
    composition: str | None = None,
) -> list[Path]:
    """Write the Modelica interface package and return every file, sorted.

    ``output_dir/<package>/`` holds ``package.mo``, ``package.order``,
    ``Interfaces.mo`` (the four primitive input/output aliases), and
    ``GeneratedInterfaces.mo`` (one connector per port definition). The
    subpackages are declared inside the root package, so ``within`` nests them.
    """
    architecture = _architecture(source)
    definitions = _port_definitions(
        components(architecture, composition=composition)
    )

    root = Path(output_dir) / package
    parent = _parent_scope(package, within)
    files = {
        root / "package.mo": _package_text(package, within),
        root / "package.order": _order_text(),
        root / f"{INTERFACES}.mo": _interfaces_text(parent),
        root / f"{GENERATED}.mo": _generated_text(parent, definitions),
    }
    for path, text in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return sorted(files)
