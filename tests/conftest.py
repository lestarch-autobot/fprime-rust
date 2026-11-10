"""Shared fixtures: a self-contained subset of the F Prime FPP model and fixture components"""
from __future__ import annotations

from pathlib import Path
from typing import List

import pytest

FIXTURES = Path(__file__).parent / "fixtures"
FPRIME = FIXTURES / "fprime"
COMPONENTS = FIXTURES / "components"


def framework_closure() -> List[Path]:
    """Every framework FPP file in the fixture subset, sorted for determinism"""
    return sorted(path for path in FPRIME.rglob("*.fpp*") if path.is_file())


def write_cache(build_dir: Path, paths: List[Path]) -> Path:
    """Write an fpp-cache/stdout.txt listing ``paths`` under ``build_dir``"""
    cache = build_dir / "fpp-cache" / "stdout.txt"
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text("".join(f"{path}\n" for path in paths), encoding="utf-8")
    return cache


@pytest.fixture
def build_dir(tmp_path: Path) -> Path:
    """A module build directory whose closure cache lists the fixture framework"""
    write_cache(tmp_path, framework_closure())
    return tmp_path


@pytest.fixture
def prefixes() -> List[Path]:
    return [FIXTURES]
