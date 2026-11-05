"""Deterministic packaging of an already-built FMU directory.

This module drives the archive, not the compiler. An FMU is a directory tree
(``modelDescription.xml``, ``binaries/<platform>/``, optional ``sources/``,
``resources/``, ``documentation/``); :func:`stage_fmu` lays that tree out and
:func:`package_fmu` writes it as a ``.fmu`` zip with the FMI epoch timestamp,
sorted entries, and the library executable bit that the FMI 2.0 checklist
requires.

Validation stops the two mismatches that produce an FMU a tool cannot load:
an interface ``modelIdentifier`` that does not name the binary, and a platform
token that is not on the supported allow-list.
"""

from __future__ import annotations

import re
import shutil
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from pyssp_standard.common.archive.archive import package_archive
from pyssp_standard.standard.fmi2.codec import Fmi2ModelDescriptionXmlCodec
from pyssp_standard.standard.fmi2.model.model_description import (
    Fmi2ModelDescriptionDocument,
)

#: Platform directory names this packager emits. The token check accepts any
#: safe name; membership here decides whether the archive may be written.
SUPPORTED_PLATFORMS = frozenset({"linux64"})

_PLATFORM_TOKEN = re.compile(r"^[A-Za-z0-9_]+$")
_CODEC = Fmi2ModelDescriptionXmlCodec()


def _validate_platform(platform: str) -> str:
    """Check the platform directory token before it becomes a path component."""
    if not _PLATFORM_TOKEN.fullmatch(platform):
        raise ValueError(
            f"platform {platform!r} must match ^[A-Za-z0-9_]+$ and contain no "
            "path separator (for example 'linux64')"
        )
    if platform not in SUPPORTED_PLATFORMS:
        supported = ", ".join(sorted(SUPPORTED_PLATFORMS))
        raise ValueError(
            f"platform {platform!r} is not supported; supported platforms: "
            f"{supported}"
        )
    return platform


def _require_file(path: Path, role: str) -> None:
    if not path.is_file():
        raise ValueError(f"{role} {path} does not exist or is not a file")


def _require_entry(path: Path, role: str) -> None:
    if not path.exists():
        raise ValueError(f"{role} {path} does not exist")


def _load_model_description(
    path: Path,
) -> tuple[Fmi2ModelDescriptionDocument, bytes]:
    """Parse the model description once and keep the exact bytes to copy."""
    _require_file(path, "modelDescription")
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(
            f"modelDescription {path} is not UTF-8 XML: {exc}"
        ) from exc
    try:
        document = _CODEC.parse(text)
    except (ET.ParseError, KeyError, ValueError) as exc:
        raise ValueError(
            f"modelDescription {path} is not a valid FMI 2.0 XML document: {exc}"
        ) from exc
    return document, raw


def _validate_model_description(
    document: Fmi2ModelDescriptionDocument, path: Path, binary: Path
) -> None:
    if document.fmi_version != "2.0":
        raise ValueError(
            f"modelDescription {path} declares fmiVersion="
            f"{document.fmi_version!r}; pyfmi_sysml2 packages FMI 2.0 only"
        )
    if document.interface_type is None or document.capabilities is None:
        raise ValueError(
            f"modelDescription {path} has no ModelExchange/CoSimulation "
            "element; an FMU needs one interface that declares modelIdentifier"
        )
    identifier = document.capabilities.model_identifier
    if identifier != binary.stem:
        raise ValueError(
            f"modelIdentifier {identifier!r} does not match binary stem "
            f"{binary.stem!r}; name the binary {identifier!r}<suffix>"
        )


def _prepare_directory(directory: Path, overwrite: bool) -> None:
    """Create an empty staging directory, refusing to mix with old files."""
    if directory.exists():
        if not directory.is_dir():
            raise NotADirectoryError(
                f"staging path {directory} exists and is not a directory"
            )
        if any(directory.iterdir()):
            if not overwrite:
                raise FileExistsError(
                    f"staging directory {directory} is not empty; pass "
                    "overwrite=True to replace its contents"
                )
            shutil.rmtree(directory)
    directory.mkdir(parents=True, exist_ok=True)


def _copy_file(source: Path, root: Path, role: str) -> Path:
    _require_file(source, role)
    root.mkdir(parents=True, exist_ok=True)
    destination = root / source.name
    if destination.exists():
        raise ValueError(
            f"duplicate {role} name {source.name!r} under {root.name}/"
        )
    shutil.copyfile(source, destination)
    return destination


def _copy_entry(source: Path, root: Path, role: str) -> Path:
    """Copy a file or a whole directory tree under ``root``."""
    _require_entry(source, role)
    root.mkdir(parents=True, exist_ok=True)
    destination = root / source.name
    if destination.exists():
        raise ValueError(
            f"duplicate {role} name {source.name!r} under {root.name}/"
        )
    if source.is_dir():
        shutil.copytree(source, destination)
    else:
        shutil.copyfile(source, destination)
    return destination


def stage_fmu(
    directory: str | Path,
    *,
    model_description: str | Path,
    binary: str | Path,
    platform: str = "linux64",
    headers: tuple[str | Path, ...] | list[str | Path] = (),
    resources: tuple[str | Path, ...] | list[str | Path] = (),
    documentation: tuple[str | Path, ...] | list[str | Path] = (),
    overwrite: bool = False,
) -> Path:
    """Write a clean FMU tree at *directory* and return it.

    The model description is copied verbatim to the archive root, the binary to
    ``binaries/<platform>/``, each header to ``sources/``, each resource entry
    to ``resources/`` (directories recursively), and each documentation entry to
    ``documentation/``. Empty optional groups produce no directory.

    Args:
        directory: Staging directory. It must be empty (or absent) unless
            *overwrite* is true, in which case its contents are replaced.
        model_description: Path to the FMI 2.0 ``modelDescription.xml``.
        binary: Built shared library. Its stem must equal the interface
            ``modelIdentifier``.
        platform: Platform directory token, from :data:`SUPPORTED_PLATFORMS`.
        headers: Generated C headers for ``sources/``.
        resources: Files or directories for ``resources/``.
        documentation: Files or directories for ``documentation/``.
        overwrite: Replace the contents of a non-empty *directory*.

    Raises:
        ValueError: The platform token, model description, or binary name does
            not satisfy the FMU contract.
        FileExistsError: *directory* is non-empty and *overwrite* is false.
    """
    platform = _validate_platform(platform)
    directory = Path(directory)
    description_path = Path(model_description)
    binary_path = Path(binary)
    header_paths = tuple(Path(entry) for entry in headers)
    resource_paths = tuple(Path(entry) for entry in resources)
    documentation_paths = tuple(Path(entry) for entry in documentation)

    document, description_bytes = _load_model_description(description_path)
    _require_file(binary_path, "binary")
    _validate_model_description(document, description_path, binary_path)

    for header in header_paths:
        _require_file(header, "header")
    for entry in resource_paths:
        _require_entry(entry, "resource")
    for entry in documentation_paths:
        _require_entry(entry, "documentation entry")

    _prepare_directory(directory, overwrite)
    (directory / "modelDescription.xml").write_bytes(description_bytes)

    staged_binary = _copy_file(
        binary_path, directory / "binaries" / platform, "binary"
    )
    staged_binary.chmod(staged_binary.stat().st_mode | 0o111)
    for header in header_paths:
        _copy_file(header, directory / "sources", "header")
    for entry in resource_paths:
        _copy_entry(entry, directory / "resources", "resource")
    for entry in documentation_paths:
        _copy_entry(entry, directory / "documentation", "documentation entry")

    return directory


def _verify_archive(
    archive: Path, platform: str, binary: Path
) -> Path:
    """Confirm the two entries a consumer looks up without reading the XML."""
    required = {
        "modelDescription.xml",
        f"binaries/{platform}/{binary.name}",
    }
    with zipfile.ZipFile(archive) as bundle:
        present = set(bundle.namelist())
    missing = sorted(required - present)
    if missing:
        raise ValueError(
            f"packaged archive {archive} is missing {', '.join(missing)}; "
            "modelDescription.xml must be at the root and the binary under "
            "binaries/<platform>/"
        )
    return archive


def package_fmu(
    output: str | Path,
    *,
    model_description: str | Path,
    binary: str | Path,
    platform: str = "linux64",
    headers: tuple[str | Path, ...] | list[str | Path] = (),
    resources: tuple[str | Path, ...] | list[str | Path] = (),
    documentation: tuple[str | Path, ...] | list[str | Path] = (),
    stage_dir: str | Path | None = None,
) -> Path:
    """Stage the FMU tree and write the deterministic ``.fmu`` archive.

    A temporary staging directory is used unless *stage_dir* is given; in both
    cases the directory is cleared first, so it holds only this call's tree.
    Entries are sorted, every timestamp is the FMI epoch (2000-01-01), metadata
    files are mode ``0o644``, and files under ``binaries/`` are ``0o755``.
    """
    inputs = {
        "model_description": model_description,
        "binary": binary,
        "platform": platform,
        "headers": headers,
        "resources": resources,
        "documentation": documentation,
    }
    output_path = Path(output)
    binary_path = Path(binary)

    if stage_dir is None:
        with tempfile.TemporaryDirectory(prefix="pyfmi_sysml2-fmu-") as tmp:
            stage = stage_fmu(Path(tmp) / "fmu", overwrite=True, **inputs)
            archive = package_archive(stage, output_path)
    else:
        stage = stage_fmu(Path(stage_dir), overwrite=True, **inputs)
        archive = package_archive(stage, output_path)

    return _verify_archive(archive, str(platform), binary_path)
