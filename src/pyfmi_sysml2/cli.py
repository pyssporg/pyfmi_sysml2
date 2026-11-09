"""The ``pyfmi`` command line: one subcommand per generated artifact.

The four generators share a single shape here so the shell surface does not
drift from the Python surface: a source path in, an output location out, and one
line per written path on stdout. Argument errors are argparse's (exit 2),
generation and validation errors are reported without a traceback (exit 1), and
anything unexpected is left to propagate.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from pyfmi_sysml2.c_interface import generate_c_headers
from pyfmi_sysml2.model_description import (
    GENERATION_TIME_FORMAT,
    generate_model_description,
)
from pyfmi_sysml2.modelica import DEFAULT_PACKAGE, generate_modelica
from pyfmi_sysml2.package import package_fmu

#: Where the three generators write when no ``-o/--output`` is given.
DEFAULT_OUTPUT = "build"

#: Handled failures: authored-model errors and missing inputs.
GENERATION_ERRORS = (ValueError, KeyError, FileNotFoundError)


def _parse_generation_time(text: str) -> datetime:
    """The FMI ``dateTime`` forms accepted on the command line, as UTC.

    The canonical form is the one the generator emits. An ISO 8601 form with an
    explicit offset is also accepted. A naive time is refused, because the
    artifact would then depend on the host's locality.
    """
    value = text.strip()
    if value.endswith("Z"):
        try:
            moment = datetime.strptime(value, GENERATION_TIME_FORMAT)
        except ValueError:
            pass
        else:
            return moment.replace(tzinfo=timezone.utc)

    try:
        moment = datetime.fromisoformat(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"invalid generation time {text!r}; use "
            "YYYY-MM-DDTHH:MM:SSZ or an ISO 8601 form with an offset"
        ) from None
    if moment.tzinfo is None or moment.utcoffset() is None:
        raise argparse.ArgumentTypeError(
            f"generation time {text!r} must carry a timezone, for example "
            "2026-01-01T00:00:00Z"
        )
    return moment.astimezone(timezone.utc)


def _print_paths(written: list[Path]) -> None:
    for path in written:
        print(path)


def _run_model_description(args: argparse.Namespace) -> int:
    written = generate_model_description(
        args.source,
        args.output,
        composition=args.composition,
        component=args.component,
        generation_time=args.generation_time,
        base_index=args.base_index,
    )
    _print_paths(written)
    return 0


def _run_c_headers(args: argparse.Namespace) -> int:
    written = generate_c_headers(
        args.source,
        args.output,
        composition=args.composition,
        prefix=args.prefix,
        base_index=args.base_index,
    )
    _print_paths(written)
    return 0


def _run_modelica(args: argparse.Namespace) -> int:
    written = generate_modelica(
        args.source,
        args.output,
        package=args.package,
        within=args.within,
        composition=args.composition,
    )
    _print_paths(written)
    return 0


def _run_package(args: argparse.Namespace) -> int:
    archive = package_fmu(
        args.output,
        model_description=args.model_description,
        binary=args.binary,
        platform=args.platform,
        headers=args.header,
        resources=args.resource,
        documentation=args.documentation,
    )
    _print_paths([archive])
    return 0


def _message(error: BaseException) -> str:
    """``KeyError`` stringifies with quotes; the message is what matters."""
    if isinstance(error, KeyError) and error.args:
        return str(error.args[0])
    return str(error)


def _add_source(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "source",
        metavar="SOURCE",
        help="A .sysml file or a directory containing them.",
    )


def _add_output(parser: argparse.ArgumentParser, help_text: str) -> None:
    parser.add_argument(
        "-o",
        "--output",
        metavar="OUT",
        default=DEFAULT_OUTPUT,
        help=help_text,
    )


def _add_composition(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--composition",
        metavar="NAME",
        help="Composition part definition to export (default: the single root).",
    )


def _add_base_index(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--base-index",
        metavar="N",
        type=int,
        default=0,
        help=(
            "First emitted array index (default: 0; 1 targets OMC-built "
            "Modelica FMUs, which declare arrays one-based)."
        ),
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pyfmi",
        description=(
            "Generate FMI 2.0 CoSimulation artifacts from a SysML v2 "
            "architecture."
        ),
        epilog=(
            "The three generators write to build/ unless -o/--output is given; "
            "pyfmi package requires an output archive path."
        ),
    )
    subparsers = parser.add_subparsers(
        dest="command", required=True, metavar="COMMAND"
    )

    description = subparsers.add_parser(
        "model-description",
        help="Write modelDescription.xml per component.",
        description=(
            "Write modelDescription.xml per component to an output directory."
        ),
    )
    _add_source(description)
    _add_output(
        description, "Output directory (default: build)."
    )
    _add_composition(description)
    _add_base_index(description)
    description.add_argument(
        "--component",
        metavar="NAME",
        help="Restrict the output to one exported component.",
    )
    description.add_argument(
        "--generation-time",
        metavar="ISO8601",
        type=_parse_generation_time,
        help=(
            "Fixed generationDateAndTime, for example 2026-01-01T00:00:00Z "
            "(default: now)."
        ),
    )
    description.set_defaults(handler=_run_model_description)

    headers = subparsers.add_parser(
        "c-headers",
        help="Write C interface headers.",
        description="Write the C interface headers to an output directory.",
    )
    _add_source(headers)
    _add_output(headers, "Output directory (default: build).")
    _add_composition(headers)
    _add_base_index(headers)
    headers.add_argument(
        "--prefix",
        metavar="NAME",
        help="Header prefix and C type prefix (default: the package name).",
    )
    headers.set_defaults(handler=_run_c_headers)

    modelica = subparsers.add_parser(
        "modelica",
        help="Write a Modelica interface package.",
        description=(
            "Write the Modelica interface package to an output directory."
        ),
    )
    _add_source(modelica)
    _add_output(modelica, "Output directory (default: build).")
    _add_composition(modelica)
    modelica.add_argument(
        "--package",
        metavar="NAME",
        default=DEFAULT_PACKAGE,
        help=f"Root Modelica package name (default: {DEFAULT_PACKAGE}).",
    )
    modelica.add_argument(
        "--within",
        metavar="NAME",
        help="Enclosing Modelica scope for the root package.",
    )
    modelica.set_defaults(handler=_run_modelica)

    package = subparsers.add_parser(
        "package",
        help="Write a deterministic .fmu archive.",
        description="Write a deterministic .fmu archive to the output path.",
    )
    package.add_argument(
        "-o",
        "--output",
        metavar="OUT",
        required=True,
        help="Output .fmu archive path (required).",
    )
    package.add_argument(
        "--model-description",
        metavar="PATH",
        required=True,
        help="FMI 2.0 modelDescription.xml for the archive root.",
    )
    package.add_argument(
        "--binary",
        metavar="PATH",
        required=True,
        help="Built shared library; its stem must be the modelIdentifier.",
    )
    package.add_argument(
        "--platform",
        metavar="NAME",
        default="linux64",
        help="Platform directory under binaries/ (default: linux64).",
    )
    package.add_argument(
        "--header",
        metavar="PATH",
        action="append",
        default=[],
        help="Generated header to include under sources/ (repeatable).",
    )
    package.add_argument(
        "--resource",
        metavar="PATH",
        action="append",
        default=[],
        help="File or directory to include under resources/ (repeatable).",
    )
    package.add_argument(
        "--documentation",
        metavar="PATH",
        action="append",
        default=[],
        help="File or directory to include under documentation/ (repeatable).",
    )
    package.set_defaults(handler=_run_package)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Run one ``pyfmi`` command and return its process exit code."""
    args = _parser().parse_args(argv)
    try:
        return args.handler(args)
    except GENERATION_ERRORS as error:
        print(f"pyfmi: {_message(error)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
