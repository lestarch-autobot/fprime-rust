"""UT-AC-1, UT-AC-4..UT-AC-8: generator output, name table, type table, workspace, determinism, dry-run"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Dict, List

import pytest

from conftest import COMPONENTS, FIXTURES, framework_closure, write_cache
from fprime_rust.autocode import names
from fprime_rust.autocode.__main__ import bindings_files, component_specs, main, parse_member
from fprime_rust.autocode.crate import workspace_files
from fprime_rust.autocode.model import load_module_model
from fprime_rust.autocode.view import ModelView, UnsupportedElement

RICH = COMPONENTS / "Rich.fpp"


def rich_view(build_dir: Path):
    model = load_module_model(build_dir, [RICH])
    views = ModelView(model, [FIXTURES]).views()
    assert [view.qualified_name for view in views] == ["Fx.Rich"]
    return views[0]


def module_with(tmp_path: Path, body: str) -> Path:
    unit = tmp_path / "Mod.fpp"
    unit.write_text(body, encoding="utf-8")
    write_cache(tmp_path, framework_closure() + [unit])
    return unit


def digest(files: Dict[Path, str]) -> Dict[Path, str]:
    return {path: hashlib.sha256(content.encode()).hexdigest() for path, content in files.items()}


def by_name(items, name):
    return next(item for item in items if item.name == name)


# UT-AC-1 ------------------------------------------------------------------------------------------------------

def test_annotated_component_emits_shim_base_and_template(build_dir: Path, tmp_path: Path):
    out = tmp_path / "out"
    files = bindings_files(build_dir, out, [FIXTURES], [RICH])
    assert set(files) == {out / "Rich.hpp", out / "Rich.cpp", out / "rich_base.rs", out / "Rich.template.rs",
                          COMPONENTS / "Rich.rs"} - ({COMPONENTS / "Rich.rs"} if (COMPONENTS / "Rich.rs").exists() else set())
    assert re.search(r"class Rich final :\s+public RichComponentBase", files[out / "Rich.hpp"])
    assert "pub trait Component" in files[out / "rich_base.rs"]
    assert "impl Component for" in files[out / "Rich.template.rs"]


def test_unannotated_component_and_annotated_port_or_module_emit_nothing(tmp_path: Path):
    unit = module_with(tmp_path, """
module Fx {
  @ fprime-rust
  port Ann(a: U32)
  @ fprime-rust
  module Inner { constant k = 1 }
  passive component Plain { sync input port p: Ann }
}
""")
    assert bindings_files(tmp_path, tmp_path / "out", [FIXTURES], [unit]) == {}
    assert component_specs(tmp_path, tmp_path / "out", [FIXTURES], [unit]) == []


def test_module_without_annotation_is_a_no_op_without_loading_the_closure(tmp_path: Path):
    unit = tmp_path / "Plain.fpp"
    unit.write_text("module Fx { passive component Plain { } }", encoding="utf-8")
    assert bindings_files(tmp_path, tmp_path / "out", [FIXTURES], [unit]) == {}


# UT-AC-4 ------------------------------------------------------------------------------------------------------

def test_name_table(build_dir: Path):
    view = rich_view(build_dir)
    assert view.ffi_prefix == "fprime_rust_Fx_Rich"
    v_in = by_name(view.input_ports, "vIn")
    a_in = by_name(view.input_ports, "aIn")
    v_out = by_name(view.output_ports, "vOut")
    ip = by_name(view.internal_ports, "ip")
    ac = by_name(view.commands, "AC")
    e1 = by_name(view.events, "E1")
    e2 = by_name(view.events, "E2")
    t1 = by_name(view.channels, "T1")
    p1 = by_name(view.parameters, "P1")
    table = [
        (names.cpp_handler(v_in), names.handler(view, v_in), names.rust_handler(v_in),
         "vIn_handler", "fprime_rust_Fx_Rich_vIn_handler", "vIn_handler"),
        (names.cpp_out(v_out), names.out(view, v_out), names.rust_out(v_out),
         "vOut_out", "fprime_rust_Fx_Rich_vOut_out", "vOut_out"),
        (names.cpp_internal_handler(ip), names.internal_handler(view, ip), names.rust_internal_handler(ip),
         "ip_internalInterfaceHandler", "fprime_rust_Fx_Rich_ip_internal_handler", "ip_internal_handler"),
        (names.cpp_internal_invoke(ip), names.internal_invoke(view, ip), names.rust_internal_invoke(ip),
         "ip_internalInterfaceInvoke", "fprime_rust_Fx_Rich_ip_internal_invoke", "ip_internal_invoke"),
        (names.cpp_overflow_hook(a_in), names.overflow_hook(view, a_in), names.rust_overflow_hook(a_in),
         "aIn_overflowHook", "fprime_rust_Fx_Rich_aIn_overflow_hook", "aIn_overflow_hook"),
        (names.cpp_overflow_hook(ac), names.overflow_hook(view, ac), names.rust_overflow_hook(ac),
         "AC_cmdOverflowHook", "fprime_rust_Fx_Rich_AC_overflow_hook", "AC_overflow_hook"),
        (names.cpp_cmd_handler(ac), names.cmd_handler(view, ac), names.rust_cmd_handler(ac),
         "AC_cmdHandler", "fprime_rust_Fx_Rich_AC_cmd_handler", "AC_cmd_handler"),
        (names.cpp_log(e1), names.log(view, e1), names.rust_log(e1),
         "log_WARNING_LO_E1", "fprime_rust_Fx_Rich_log_WARNING_LO_E1", "log_WARNING_LO_E1"),
        (names.cpp_log(e2), names.log(view, e2), names.rust_log(e2),
         "log_FATAL_E2", "fprime_rust_Fx_Rich_log_FATAL_E2", "log_FATAL_E2"),
        (names.cpp_tlm_write(t1), names.tlm_write(view, t1), names.rust_tlm_write(t1),
         "tlmWrite_T1", "fprime_rust_Fx_Rich_tlmWrite_T1", "tlmWrite_T1"),
        (names.cpp_param_get(p1), names.param_get(view, p1), names.rust_param_get(p1),
         "paramGet_P1", "fprime_rust_Fx_Rich_paramGet_P1", "paramGet_P1"),
    ]
    for cpp, ffi, rust, cpp_expected, ffi_expected, rust_expected in table:
        assert (cpp, ffi, rust) == (cpp_expected, ffi_expected, rust_expected)
    assert names.parameter_updated(view) == "fprime_rust_Fx_Rich_parameter_updated"
    assert names.num_msgs_dropped(view) == "fprime_rust_Fx_Rich_num_msgs_dropped"
    assert [names.lifecycle(view, step) for step in ("new", "init", "drop")] == [
        "fprime_rust_Fx_Rich_new", "fprime_rust_Fx_Rich_init", "fprime_rust_Fx_Rich_drop"]
    assert view.base_module == "rich_base"


# UT-AC-5 ------------------------------------------------------------------------------------------------------

def test_type_table(build_dir: Path):
    view = rich_view(build_dir)
    v_in = by_name(view.input_ports, "vIn")
    a, s, m = v_in.params
    assert (a.type.rust, a.type.cpp) == ("u32", "U32")
    assert (s.type.rust, s.type.cpp, s.type.string_size, s.is_ref) == ("&str", "Fw::StringBase", "20", False)
    assert (m.type.rust, m.type.kind, m.type.cpp) == ("Mode", "enum", "Fx::Mode"), "type-table row `enum E` -> `E`"
    assert v_in.returns.rust == "u32", "alias `type Count = U32` maps to u32"
    assert by_name(view.channels, "T1").type.rust == "f64"
    assert by_name(view.channels, "T3").type.rust == "Mode"
    b, s40 = by_name(view.events, "E1").params
    assert (b.type.rust, b.type.ffi) == ("bool", "u8")
    assert (s40.type.rust, s40.type.string_size) == ("&str", "40")
    assert by_name(view.parameters, "P1").type.rust == "u32"
    assert view.platform_types["FwIndexType"] in ("i16", "i32", "i64")


REJECTED = {
    "serial port": "sync input port ser: serial",
    "state machine": "state machine S { initial enter I \n state I }\n state machine instance sm: S",
    "data product container": "time get port timeGetOut\n product send port productSendOut\n"
                              " product get port productGetOut\n product record R: U32\n product container C",
    "struct argument": "sync input port sp: SP",
    "array return": "sync input port ap: AP",
    "Fw.Buffer argument": "sync input port bp: Fw.BufferSend",
    "Fw.ComBuffer argument": "sync input port cp: Fw.Com",
}


@pytest.mark.parametrize("element", sorted(REJECTED))
def test_unsupported_elements_are_rejected_by_qualified_name(tmp_path: Path, element: str):
    unit = module_with(tmp_path, f"""
module Fx {{
  struct St {{ a: U32 }}
  array Arr = [2] U32
  port SP(s: St)
  port AP -> Arr
  @ fprime-rust
  {"active" if element == "state machine" else "passive"} component Bad {{
    {REJECTED[element]}
  }}
}}
""")
    with pytest.raises(UnsupportedElement, match=r"^unsupported element Fx\.Bad") as info:
        bindings_files(tmp_path, tmp_path / "out", [FIXTURES], [unit])
    assert "Fx.Bad" in str(info.value)


# UT-AC-6 ------------------------------------------------------------------------------------------------------

def test_workspace_has_one_member_per_component_and_a_staticlib_root(tmp_path: Path):
    members = [parse_member(f"Ns.{name}=/gen/{name.lower()}_base.rs=/src/{name}.rs") for name in ("A", "B")]
    files = workspace_files(tmp_path, "Deploy", Path("/runtime"), members)
    manifest = files[tmp_path / "Cargo.toml"]
    assert "[workspace]" in manifest and 'members = ["ns_a", "ns_b", "fprime_rust_Deploy"]' in manifest
    root = files[tmp_path / "fprime_rust_Deploy" / "Cargo.toml"]
    assert 'crate-type = ["staticlib"]' in root and 'name = "fprime_rust_Deploy"' in root
    lib = files[tmp_path / "fprime_rust_Deploy" / "src" / "lib.rs"]
    assert "pub use ns_a;" in lib and "pub use ns_b;" in lib
    assert len(files) == 1 + 2 * (len(members) + 1)
    for member in members:
        member_manifest = files[tmp_path / member.name / "Cargo.toml"]
        assert 'crate-type = ["rlib"]' in member_manifest
        assert 'panic = "abort"' in manifest


# UT-AC-7 ------------------------------------------------------------------------------------------------------

def test_two_runs_are_byte_identical(build_dir: Path, tmp_path: Path):
    out = tmp_path / "out"
    first = digest(bindings_files(build_dir, out, [FIXTURES], [RICH]))
    second = digest(bindings_files(build_dir, out, [FIXTURES], [RICH]))
    assert first == second and first
    members = [parse_member("Fx.Rich=/gen/rich_base.rs=/src/Rich.rs")]
    assert digest(workspace_files(out, "D", Path("/r"), members)) == digest(workspace_files(out, "D", Path("/r"), members))


# UT-AC-8 ------------------------------------------------------------------------------------------------------

def test_dry_run_lists_exactly_the_files_written(build_dir: Path, tmp_path: Path, capsys, monkeypatch):
    out = tmp_path / "out"
    seed = tmp_path / "src" / "Rich.rs"
    seed.parent.mkdir()
    unit = tmp_path / "src" / "Rich.fpp"
    unit.write_text(RICH.read_text(encoding="utf-8"), encoding="utf-8")
    write_cache(build_dir, framework_closure() + [unit])
    args = ["bindings", str(build_dir), "--output-directory", str(out), "--prefixes", str(FIXTURES), str(tmp_path),
            "--translation-units", str(unit)]
    assert main(args + ["--dry-run"]) == 0
    listed = sorted(Path(line) for line in capsys.readouterr().out.splitlines() if line.strip())
    assert not out.exists() and not seed.exists()
    assert main(args) == 0
    written = sorted(list(out.iterdir()) + [seed])
    assert listed == written
    assert seed.read_text() == (out / "Rich.template.rs").read_text()


def test_overflow_hooks_never_borrow_the_implementation(build_dir: Path, tmp_path: Path):
    """Ruling 6 regression: hook entries get no `fpr_impl` and create no `&mut Implementation` (the invoking handler
    may hold one), on the C++ and the Rust side"""
    out = tmp_path / "out"
    files = bindings_files(build_dir, out, [FIXTURES], [RICH])
    base, cpp = files[out / "rich_base.rs"], files[out / "Rich.cpp"]
    hooks = [block for block in base.split("#[no_mangle]") if "_overflow_hook(" in block.split("{", 1)[0]]
    assert hooks, "the Rich fixture declares hook members"
    for block in hooks:
        assert "fpr_impl" not in block and "&mut *(" not in block
        assert "Implementation::" in block
    assert "_overflow_hook(&mut self" not in base
    for line in cpp.splitlines():
        if "_overflow_hook(" in line and "::" not in line:
            assert "this->m_impl" not in line
