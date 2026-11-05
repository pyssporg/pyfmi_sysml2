"""Shared test configuration and the fixed clock every golden is built with."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

import pytest

#: The injected clock. Goldens must never depend on the wall clock.
GENERATION_TIME = datetime(2026, 1, 1, tzinfo=timezone.utc)

#: The injected clock as the CLI text form.
GENERATION_TIME_TEXT = "2026-01-01T00:00:00Z"

FIXTURE_ROOT = Path(__file__).parent / "fixtures"
GOLDEN_ROOT = Path(__file__).parent / "golden"


def fixture_path(subject: str, name: str) -> Path:
    """Path of one architecture fixture file."""
    return FIXTURE_ROOT / subject / name


@pytest.fixture(name="generation_time")
def generation_time_fixture() -> datetime:
    return GENERATION_TIME


def update_goldens() -> bool:
    """Whether a test may rewrite its golden instead of comparing."""
    if os.environ.get("CI"):
        return False
    return os.environ.get("UPDATE_GOLDENS") == "1"
