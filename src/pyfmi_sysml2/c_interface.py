"""C interface headers for the FMI components of an architecture.

One pair of files is written per architecture: a common header with the port
payload structs and the value-reference mapping type, and one header per
component with its FMI guid macro, its value-reference enum and its C++
instance helper.

The common header is plain C11: it is the part a C simulator may include to
read the mapping a C++ host filled in. Only the instance helper is C++, because
FMI 2.0 needs the storage and the mapping to be laid out together.
"""

from __future__ import annotations

from collections.abc import Sequence
from os import PathLike
from pathlib import Path

from pycps_sysml2 import Architecture, load

from pyfmi_sysml2.interface import (
    DATA_TYPE_TAGS,
    Component,
    Field,
    Variable,
    c_type,
    components,
    export_identity,
    resolve_system,
    sanitize_identifier,
)
from pyfmi_sysml2.model_description import component_guid

#: Default for a member whose declaration carries no authored start value.
IMPLICIT_DEFAULT = "{}"

#: Marker that starts and ends the C++-only section of a header.
CPP_BEGIN = "#ifdef __cplusplus"
CPP_END = "#endif  /* __cplusplus */"

#: C11 and C++17 keywords; a port field or parameter may not use them as a
#: struct member name, so the emitter appends ``_`` (``auto`` -> ``auto_``).
#: The SysML field name and the FMI variable name are unaffected; only the C
#: spelling of the member differs.
RESERVED = frozenset(
    """
    _Alignas _Alignof _Atomic _Bool _Complex _Generic _Imaginary _Noreturn
    _Static_assert _Thread_local alignas alignof and and_eq asm auto bitand
    bitor bool break case catch char char8_t char16_t char32_t class compl
    concept const consteval constexpr constinit const_cast continue co_await
    co_return co_yield decltype default delete do double dynamic_cast else
    enum explicit export extern false float for friend goto if inline int
    long mutable namespace new noexcept not not_eq nullptr operator or or_eq
    private protected public register reinterpret_cast requires restrict
    return short signed sizeof static static_assert static_cast struct switch
    template this thread_local throw true try typedef typeid typename union
    unsigned using virtual void volatile wchar_t while xor xor_eq
    """.split()
)


def _escape(name: str) -> str:
    """A C identifier spelling of ``name`` that is not a keyword."""
    return f"{name}_" if name in RESERVED else name


def member_expression(member: str) -> str:
    """C++ member access for a variable member, keyword-escaped."""
    escaped = []
    for part in member.split("."):
        base, bracket, index = part.partition("[")
        escaped.append(f"{_escape(base)}{bracket}{index}")
    return ".".join(escaped)


def common_header_name(package: str) -> str:
    """File name of the architecture-wide header."""
    return f"{package}_InterfaceCommon.h"


def header_stem(package: str, component: str, *, direct: bool = False) -> str:
    """The ``<package>_<component>`` stem the C symbols are built from.

    A direct FMU model is named after its package, so repeating that name
    would yield ``Generator_Generator`` for the only component in the build.
    Only the direct case collapses the shared name; a container keeps the full
    stem, even when its component happens to share the package name.
    """
    if direct and package == component:
        return component
    return f"{package}_{component}"


def component_header_name(
    package: str, component: str, *, direct: bool = False
) -> str:
    """File name of one component header."""
    return f"{header_stem(package, component, direct=direct)}.h"


def _data_type_tag(package: str, type_name: str) -> str:
    """``<PKG>_DATA_<TAG>`` for an FMI primitive."""
    tag = DATA_TYPE_TAGS.get(type_name, "REAL")
    return f"{sanitize_identifier(package)}_DATA_{tag}"


def _field_declaration(field: Field) -> str:
    """C declaration line for one port payload field."""
    storage = c_type(field.type_name)
    name = _escape(field.name)
    if field.array is None:
        return f"  {storage} {name};"
    return f"  {storage} {name}[{field.array}];"


def _default_text(variable: Variable) -> str:
    """C++ initializer for one variable's start value."""
    if variable.start_text is None:
        return IMPLICIT_DEFAULT
    if variable.type_name == "String":
        escaped = variable.start_text.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return variable.start_text


def _parameter_variable(component: Component, member: str) -> Variable | None:
    """The parameter variable stored in ``member``, if any."""
    for variable in component.variables:
        if variable.causality == "parameter" and variable.member == member:
            return variable
    return None


def _parameter_member(component: Component, field: Field) -> str:
    """C++ member declaration for one parameter, with its default."""
    storage = c_type(field.type_name, cpp=True)
    name = _escape(field.name)
    if field.array is None:
        variable = _parameter_variable(component, field.name)
        default = IMPLICIT_DEFAULT if variable is None else _default_text(variable)
        return f"  {storage} {name} = {default};"

    elements = [
        _parameter_variable(component, f"{field.name}[{index}]")
        for index in range(
            field.base_index, field.base_index + field.array
        )
    ]
    if any(element is None for element in elements):
        return f"  {storage} {name}[{field.array}] = {IMPLICIT_DEFAULT};"
    values = ", ".join(_default_text(element) for element in elements)
    return f"  {storage} {name}[{field.array}] = {{{values}}};"


def interface_common_header(package: str, components: Sequence[Component]) -> str:
    """Text of ``<Pkg>_InterfaceCommon.h``.

    Port definitions appear in first-use order: components are already sorted
    by name, and each component lists its ports in declaration order.
    """
    upper = sanitize_identifier(package)
    guard = f"{upper}_INTERFACECOMMON_H"
    lines = [
        f"#ifndef {guard}",
        f"#define {guard}",
        "",
        "#include <stdbool.h>",
        "#include <stddef.h>",
        "#include <stdint.h>",
        "",
        f"/* Generated from architecture package {package}. Do not edit manually. */",
        "",
    ]

    seen: set[str] = set()
    for component in components:
        for port in component.ports:
            if port.definition in seen:
                continue
            seen.add(port.definition)
            lines.append(f"typedef struct {package}_{port.definition} {{")
            for field in port.fields:
                lines.append(_field_declaration(field))
            lines.append(f"}} {package}_{port.definition};")
            lines.append("")

    lines.extend(
        [
            f"typedef enum {package}_DataType {{",
            f"  {upper}_DATA_NONE = 0,",
            f"  {upper}_DATA_REAL = 1,",
            f"  {upper}_DATA_INTEGER = 2,",
            f"  {upper}_DATA_BOOLEAN = 3,",
            f"  {upper}_DATA_STRING = 4,",
            f"}} {package}_DataType;",
            "",
            f"typedef struct {package}_VrMapping {{",
            "  void* data;",
            f"  {package}_DataType type;",
            "  bool writable;",
            f"}} {package}_VrMapping;",
            "",
            f"#endif  /* {guard} */",
            "",
        ]
    )
    return "\n".join(lines)


def component_header(
    package: str,
    component: Component,
    *,
    direct: bool = False,
    system: str | None = None,
) -> str:
    """Text of the component header (no trailing newline).

    ``system`` names the export root that scopes the ``*_GUID`` macro, so the
    macro matches the guid ``generate_model_description`` writes for the same
    component. A direct FMU model (``direct=True``) needs none, because its
    guid key has no container level; without a system the macro falls back to
    the component name, which is exact for direct models only.
    """
    stem = header_stem(package, component.name, direct=direct)
    upper = sanitize_identifier(package)
    upper_stem = sanitize_identifier(stem)
    guard = f"{upper_stem}_H"
    instance = f"{stem}_Instance"
    label = (
        package
        if direct and package == component.name
        else f"{package}.{component.name}"
    )
    guid = component_guid(system or component.name, component.name, direct=direct)
    lines = [
        f"#ifndef {guard}",
        f"#define {guard}",
        "",
        f'#include "{common_header_name(package)}"',
        "",
        f"/* Generated interface for {label}. Do not edit manually. */",
        "",
        f"#define {upper_stem}_GUID \"{guid}\"",
        "",
        f"typedef enum {stem}_ValueReference {{",
    ]
    for variable in component.variables:
        entry = f"{upper_stem}_VR_{sanitize_identifier(variable.name)}"
        lines.append(f"  {entry} = {variable.value_reference},")
    lines.extend(
        [
            f"}} {stem}_ValueReference;",
            "",
            f"enum {{ {stem}_VrCount = {component.vr_count} }};",
            "",
            CPP_BEGIN,
            "#include <string>",
            "",
            f"struct {instance} {{",
            f"  {package}_VrMapping vr_map[{component.vr_count}] = {{}};",
        ]
    )
    for field in component.parameters:
        lines.append(_parameter_member(component, field))
    for port in component.ports:
        lines.append(f"  {package}_{port.definition} {_escape(port.name)} = {{}};")
    lines.extend(["};", ""])

    lines.append(
        f"inline void {stem}_initialize_vr_map("
        f"{instance}* instance) {{"
    )
    lines.append(f"  for (size_t i = 0; i < {stem}_VrCount; ++i) {{")
    lines.append(f"    instance->vr_map[i] = {{nullptr, {upper}_DATA_NONE, false}};")
    lines.append("  }")
    for variable in component.variables:
        entry = f"{upper_stem}_VR_{sanitize_identifier(variable.name)}"
        writable = "true" if variable.writable else "false"
        lines.append(
            f"  instance->vr_map[{entry}] = "
            f"{{&instance->{member_expression(variable.member)}, "
            f"{_data_type_tag(package, variable.type_name)}, {writable}}};"
        )
    lines.extend(["}", "", CPP_END, f"#endif  /* {guard} */"])
    return "\n".join(lines)


def _architecture(source: Architecture | str | PathLike[str]) -> Architecture:
    """An already loaded architecture, or the one at ``source``."""
    if isinstance(source, Architecture):
        return source
    return load(source)


def generate_c_headers(
    source: Architecture | str | PathLike[str],
    output_dir: str | PathLike[str],
    *,
    composition: str | None = None,
    prefix: str | None = None,
    base_index: int = 0,
) -> list[Path]:
    """Write the C interface headers of ``source`` into ``output_dir``.

    ``prefix`` defaults to the architecture package name and decides the file
    names and the C type names. The returned list starts with the common
    header, followed by one component header per exported component. Each
    component header carries a ``<PREFIX>_<COMPONENT>_GUID`` macro with the
    same guid the modelDescription generator writes for that component. A
    direct FMU model whose definition names the package uses that name once.
    ``base_index`` shifts the ``[i]`` suffixes of array members in the
    generated C (default 0; 1 targets OMC-built Modelica FMUs).
    """
    architecture = _architecture(source)
    package = prefix or architecture.package_name
    system = resolve_system(architecture, composition)
    exported = components(
        architecture, composition=composition, base_index=base_index
    )
    direct = export_identity(architecture, system).direct

    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []

    common_path = directory / common_header_name(package)
    common_path.write_text(
        interface_common_header(package, exported), encoding="utf-8"
    )
    written.append(common_path)

    for item in exported:
        path = directory / component_header_name(
            package, item.name, direct=direct
        )
        path.write_text(
            component_header(
                package, item, direct=direct, system=system.name
            ),
            encoding="utf-8",
        )
        written.append(path)

    return written
