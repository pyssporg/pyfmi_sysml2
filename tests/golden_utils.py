"""Golden comparison used by every artifact test.

A golden is compared byte-for-byte. ``UPDATE_GOLDENS=1`` rewrites it, but never
under ``CI``: goldens are reviewed artifacts, not test output.
"""

from __future__ import annotations

from pathlib import Path

from conftest import update_goldens


def _write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def assert_golden_text(path: Path, text: str) -> None:
    """Compare UTF-8 text with the golden at ``path``."""
    if update_goldens():
        _write(path, text.encode("utf-8"))
        return
    assert path.is_file(), f"missing golden {path}"
    assert text == path.read_text(encoding="utf-8"), f"golden mismatch: {path}"


def assert_golden_bytes(path: Path, data: bytes) -> None:
    """Compare bytes with the golden at ``path``."""
    if update_goldens():
        _write(path, data)
        return
    assert path.is_file(), f"missing golden {path}"
    assert data == path.read_bytes(), f"golden mismatch: {path}"
