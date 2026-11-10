"""UT-BUILD-1/2 over a configured F Prime build of tests/project (set FPRIME_RUST_FIXTURE_BUILD to the build cache)

The fixture build itself takes minutes: `cd tests/project && fprime-util generate --ut && fprime-util check`, then
`FPRIME_RUST_FIXTURE_BUILD=tests/project/build-fprime-automatic-native-ut pytest tests/test_build.py`.
"""
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[1] / "tests" / "project"
BUILD = os.environ.get("FPRIME_RUST_FIXTURE_BUILD")
needs_build = pytest.mark.skipif(BUILD is None, reason="FPRIME_RUST_FIXTURE_BUILD not set")
EXECUTABLES = ["Fixtures_PassiveFix_ut_exe", "Fixtures_QueuedFix_ut_exe", "Fixtures_ActiveFix_ut_exe"]


@needs_build
@pytest.mark.parametrize("executable", EXECUTABLES)
def test_ut_build_1_one_archive_and_one_marker_per_executable(executable):
    build = Path(BUILD)
    ninja = (build / "build.ninja").read_text()
    link = next(line for line in ninja.splitlines() if f"LINK_LIBRARIES" in line and f"fprime_rust_{executable}.a" in line)
    assert link.count("libfprime_rust_") == 1, link
    symbols = subprocess.run(["nm", str(build / "bin" / "Linux" / executable)], check=True, capture_output=True, text=True).stdout
    assert len(re.findall(r" T fprime_rust_runtime_marker$", symbols, re.M)) == 1


@needs_build
def test_ut_build_2_module_without_annotation_runs_no_cargo():
    build = Path(BUILD)
    assert not (build / "Fixtures" / "Ports" / "fprime_rust").exists()
    for executable in EXECUTABLES:
        assert (build / "Fixtures" / executable.replace("Fixtures_", "").replace("_ut_exe", "") / "fprime_rust" / executable).is_dir()


@pytest.mark.skipif(shutil.which("cmake") is None, reason="cmake not on PATH")
def test_ut_build_2_missing_cargo_fails_configure_naming_it(tmp_path):
    result = subprocess.run(["cmake", str(PROJECT), "-DFPRIME_RUST_CARGO=/nonexistent/cargo", "-G", "Ninja",
                             f"-DFPRIME_FRAMEWORK_PATH={PROJECT.parents[1] / 'lib' / 'fprime'}"],
                            cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode != 0
    assert "/nonexistent/cargo" in result.stderr + result.stdout
