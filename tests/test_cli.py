"""CLI paths of fprime-rust-ac: error reporting, `components` listing, enum name collisions"""
from pathlib import Path

import pytest

from conftest import FIXTURES
from fprime_rust.autocode.__main__ import main
from test_autocode import module_with

ENUM_CLASH = """
module Fx {
  enum Mode : U8 { A, B }
  module Inner { enum Mode : U8 { C, D } }
  @ fprime-rust
  passive component Clash {
    sync input port p: Plainish
  }
  port Plainish(a: Mode, b: Inner.Mode)
}
"""


def cli(tmp_path: Path, unit: Path, command: str = "bindings"):
    return [command, str(tmp_path), "--output-directory", str(tmp_path / "out"), "--prefixes", str(FIXTURES), str(tmp_path),
            "--translation-units", str(unit)]


def test_unsupported_element_exits_one_with_error_line(tmp_path: Path, capsys):
    unit = module_with(tmp_path, "module Fx {\n  @ fprime-rust\n  passive component Bad { sync input port s: serial }\n}\n")
    assert main(cli(tmp_path, unit)) == 1
    assert capsys.readouterr().err.startswith("[ERROR] fprime-rust-ac: unsupported element Fx.Bad.s")


def test_missing_cache_exits_one_with_error_line(tmp_path: Path, capsys):
    unit = tmp_path / "Mod.fpp"
    unit.write_text("module Fx {\n  @ fprime-rust\n  passive component C { }\n}\n", encoding="utf-8")
    assert main(cli(tmp_path, unit)) == 1
    assert "[ERROR] fprime-rust-ac:" in capsys.readouterr().err


def test_components_lists_rust_components_as_crate_members(tmp_path: Path, capsys):
    unit = module_with(tmp_path, "module Fx {\n  @ fprime-rust\n  passive component Two { }\n  passive component Cpp { }\n}\n")
    assert main(cli(tmp_path, unit, "components")) == 0
    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 1 and lines[0].startswith("Fx.Two=") and lines[0].endswith("Two.rs")


def test_two_enums_with_one_simple_name_are_rejected(tmp_path: Path, capsys):
    unit = module_with(tmp_path, ENUM_CLASH)
    assert main(cli(tmp_path, unit)) == 1
    assert "Mode" in capsys.readouterr().err


@pytest.mark.parametrize("body", [
    "param P: string default \"\"\n    param get port prmGetOut\n    param set port prmSetOut\n"
    "    command recv port cmdIn\n    command reg port cmdRegOut\n    command resp port cmdResponseOut",
    "output port o: Ret",
])
def test_unsized_string_read_into_rust_is_rejected(tmp_path: Path, capsys, body: str):
    unit = module_with(tmp_path, f"module Fx {{\n  port Ret -> string\n  @ fprime-rust\n  passive component Bad {{\n    {body}\n  }}\n}}\n")
    assert main(cli(tmp_path, unit)) == 1
    assert "unsized string" in capsys.readouterr().err


def test_ref_port_parameter_is_rejected(tmp_path: Path, capsys):
    unit = module_with(tmp_path, "module Fx {\n  port Rp(ref v: U32)\n  @ fprime-rust\n  passive component Bad {\n    sync input port r: Rp\n  }\n}\n")
    assert main(cli(tmp_path, unit)) == 1
    assert "ref port parameter" in capsys.readouterr().err


def test_multiline_hook_command_generates_the_overflow_hook(tmp_path: Path):
    unit = module_with(tmp_path, "module Fx {\n  @ fprime-rust\n  active component Multi {\n    command recv port cmdIn\n"
                       "    command reg port cmdRegOut\n    command resp port cmdResponseOut\n"
                       "    @ Set it\n    async command SET(\n      limit: U32 @< the limit\n    ) opcode 0 hook\n  }\n}\n")
    assert main(cli(tmp_path, unit)) == 0
    base = (tmp_path / "out" / "multi_base.rs").read_text()
    assert "fn SET_overflow_hook(ctx: &mut HookContext<'_>, opcode: FwOpcodeType, cmd_seq: u32) -> CmdResponse;" in base
