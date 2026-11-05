"""Layering policy: what the package may import, own, and write.

The package implements the FMI half of a SysML dialect; the dialect itself is a
dependency, never a sibling. These tests hold that boundary, the module graph,
the declared runtime dependencies, and the rule that a generator writes only
where its caller says.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

try:  # Python 3.11+
    import tomllib
except ModuleNotFoundError:  # Python 3.10, the floor this package declares
    import tomli as tomllib

pytestmark = pytest.mark.static

PACKAGE = "pyfmi_sysml2"

REPO_ROOT = Path(__file__).resolve().parent.parent

SRC_ROOT = REPO_ROOT / "src"

PACKAGE_ROOT = SRC_ROOT / PACKAGE

PYPROJECT = REPO_ROOT / "pyproject.toml"

#: The dialect library is a wheel dependency; importing it would make this
#: package a fork of the parser instead of a consumer of it.
FORBIDDEN_IMPORT = "pyssp_sysml2"

#: Runtime dependencies are immutable release assets, pinned by direct URL.
DIRECT_URL = re.compile(r"^[A-Za-z0-9_.-]+ @ https://\S+$")

EXPECTED_PYTHON = ">=3.10"


def _modules() -> dict[str, Path]:
    """Every module in the package, keyed by its stem."""
    return {path.stem: path for path in sorted(PACKAGE_ROOT.glob("*.py"))}


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _imports(path: Path) -> set[str]:
    """Modules of this package that ``path`` imports, of any form."""
    modules = _modules()
    imported: set[str] = set()
    for node in ast.walk(_tree(path)):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] == PACKAGE:
                    imported.add(alias.name.split(".")[1])
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0:
                if node.module and node.module.split(".")[0] == PACKAGE:
                    imported.add(node.module.split(".")[1])
            elif node.level == 1:
                if node.module:
                    imported.add(node.module.split(".")[0])
                else:
                    imported.update(alias.name.split(".")[0] for alias in node.names)
    return imported & modules.keys() - {path.stem}


def _pyproject() -> dict:
    return tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))


def _entry_points() -> set[str]:
    """Module stems named as console-script targets; they are graph roots."""
    scripts = _pyproject().get("project", {}).get("scripts", {})
    roots = set()
    for target in scripts.values():
        module = target.split(":")[0]
        if module.split(".")[0] == PACKAGE:
            roots.add(module.split(".")[1])
    return roots


def test_sources_do_not_import_the_dialect_package():
    offenders = []
    for path in sorted(PACKAGE_ROOT.glob("*.py")):
        for node in ast.walk(_tree(path)):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            if any(name.split(".")[0] == FORBIDDEN_IMPORT for name in names):
                offenders.append(f"{path.name}:{node.lineno}")
    assert not offenders, (
        f"{FORBIDDEN_IMPORT} is a dependency, not a package this one imports: "
        f"{offenders}"
    )


def test_every_module_is_reachable_from_a_root():
    modules = _modules()
    roots = {"__init__"} | _entry_points()
    missing_roots = sorted(roots - modules.keys())
    assert not missing_roots, f"declared roots with no module: {missing_roots}"

    seen = set(roots)
    queue = list(roots)
    while queue:
        current = queue.pop()
        for imported in _imports(modules[current]):
            if imported not in seen:
                seen.add(imported)
                queue.append(imported)

    orphans = sorted(modules.keys() - seen)
    assert not orphans, (
        "modules no root reaches; import them from __init__ or delete them: "
        f"{orphans}"
    )


def test_runtime_dependencies_are_two_pinned_direct_urls():
    project = _pyproject()["project"]
    dependencies = project.get("dependencies", [])
    assert len(dependencies) == 2, (
        f"exactly two runtime dependencies expected, found {dependencies}"
    )
    wrong = [dep for dep in dependencies if not DIRECT_URL.match(dep)]
    assert not wrong, f"runtime dependencies are not direct wheel URLs: {wrong}"
    dialect = [dep for dep in dependencies if FORBIDDEN_IMPORT in dep]
    assert not dialect, f"{FORBIDDEN_IMPORT} must not be a runtime dependency: {dialect}"
    assert project.get("requires-python") == EXPECTED_PYTHON, (
        f"requires-python must stay {EXPECTED_PYTHON!r}"
    )


def test_every_module_has_a_docstring():
    missing = [
        path.name
        for path in sorted(PACKAGE_ROOT.glob("*.py"))
        if not ast.get_docstring(_tree(path))
    ]
    assert not missing, f"modules without a docstring: {missing}"


def test_generation_writes_only_where_the_caller_says():
    """No module may derive an output path from its own location."""
    offenders = []
    for path in sorted(PACKAGE_ROOT.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        for pattern in ("__file__", "getcwd(", "os.getcwd"):
            if pattern in text:
                offenders.append(f"{path.name}: {pattern}")
    assert not offenders, (
        "output paths must come from an explicit argument, not from the process: "
        f"{offenders}"
    )
