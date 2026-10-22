"""Smoke tests for quick sanity checks."""

import pytest
from scripts.check_environment import check_prerequisites


def test_smoke_environment():
    """Verifies that all prerequisites and a 60-second headless simulation pass."""
    assert check_prerequisites() is True
