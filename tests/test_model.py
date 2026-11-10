"""UT-AC-2 / UT-AC-3: model loading from fpp-cache/stdout.txt (REQ-002, -003, -004, -034)"""
from __future__ import annotations

import builtins
from pathlib import Path

import pytest

from conftest import COMPONENTS, framework_closure, write_cache
from fprime_rust.autocode.model import ModelError, load_module_model, read_closure


def test_model_loads_from_cache_without_json(build_dir: Path, monkeypatch, tmp_path: Path):
    """UT-AC-2: the model loads from the fixture cache and no JSON file is opened or written"""
    json_opened = []
    real_open = builtins.open

    def spy(file, *args, **kwargs):
        if str(file).endswith(".json"):
            json_opened.append(str(file))
        return real_open(file, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", spy)
    model = load_module_model(build_dir, [COMPONENTS / "Rich.fpp"])
    assert not model.has_errors
    assert [sym.qualified_name for sym in model.analysis.component_map] == ["Fx.Rich"]
    assert json_opened == []
    assert list(tmp_path.rglob("*.json")) == []


def test_missing_cache_names_path(tmp_path: Path):
    """UT-AC-2: a missing cache raises ModelError naming the cache path"""
    with pytest.raises(ModelError) as excinfo:
        load_module_model(tmp_path, [COMPONENTS / "Rich.fpp"])
    assert str(tmp_path / "fpp-cache" / "stdout.txt") in str(excinfo.value)


def test_empty_cache_names_path(tmp_path: Path):
    """UT-AC-2: an empty cache raises ModelError naming the cache path"""
    cache = write_cache(tmp_path, [])
    with pytest.raises(ModelError) as excinfo:
        read_closure(cache)
    assert str(cache) in str(excinfo.value) and "empty" in str(excinfo.value)


def test_unreadable_entry_names_cache_and_entry(tmp_path: Path):
    """UT-AC-2: a cache listing a nonexistent file raises ModelError naming the cache path and the entry"""
    bogus = tmp_path / "nowhere" / "Missing.fpp"
    cache = write_cache(tmp_path, framework_closure() + [bogus])
    with pytest.raises(ModelError) as excinfo:
        read_closure(cache)
    assert str(cache) in str(excinfo.value) and str(bogus) in str(excinfo.value)


def test_duplicate_source_in_closure_is_analyzed_once(build_dir: Path):
    """A translation unit that also appears in the closure is analyzed once (no duplicate definitions)"""
    rich = COMPONENTS / "Rich.fpp"
    write_cache(build_dir, framework_closure() + [rich, rich])
    model = load_module_model(build_dir, [rich])
    assert not model.has_errors


def test_undefined_symbol_fails_with_fpp_diagnostic(build_dir: Path, tmp_path: Path):
    """UT-AC-3: an undefined symbol fails with the fpp diagnostic text"""
    bad = tmp_path / "Bad.fpp"
    bad.write_text("module Bad {\n  passive component C {\n    sync input port p: NoSuchPort\n  }\n}\n")
    with pytest.raises(ModelError) as excinfo:
        load_module_model(build_dir, [bad])
    assert "symbol NoSuchPort is not defined" in str(excinfo.value)
