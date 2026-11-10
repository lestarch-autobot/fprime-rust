"""fprime_rust.autocode.rust_template:

Generates ``<Comp>.template.rs``: a compiling stub implementation of the ``Component`` trait, and seeds
``<Comp>.rs`` from it when the user file does not exist (REQ-FprimeRust-007).
"""
from __future__ import annotations

from typing import List, Optional

from . import names
from .rust_base import hook_params, rust_return_type, user_params
from .view import ComponentView, TypeInfo

QUEUED_NOTE = """// NOTE (queued component): every sync/guarded input of a Rust queued component drains the queue before
// its handler runs, on the caller's thread. Give the component exactly one sync/guarded input (its `run`)
// unless that is intended, and declare the other inputs `async`. Rust-to-Rust synchronous edges are lock
// edges and must form a DAG: break cycles with an `async` port."""


def unused_tuple(items: List[str]) -> str:
    return items[0] if len(items) == 1 else "(" + ", ".join(items) + ")"


def default_value(type_: Optional[TypeInfo]) -> str:
    if type_ is None:
        return ""
    if type_.kind == "string":
        return "String::new()"
    if type_.kind == "bool":
        return "false"
    if type_.kind == "enum":
        return f"{type_.rust}::{type_.enum.constants[0][0]}"
    return "0" if type_.kind == "int" else "0.0"


def generate(view: ComponentView) -> str:
    lines: List[str] = [f"//! `{view.qualified_name}` implementation", "",
                        f"use crate::{view.base_module}::*;", ""]
    if view.kind == "queued":
        lines += [QUEUED_NOTE, ""]
    lines += [f"/// State of `{view.qualified_name}`", "#[derive(Debug, Default)]", f"pub struct {view.name} {{}}", "",
              f"impl Component for {view.name} {{",
              "    fn new() -> Self {", f"        {view.name}::default()", "    }"]
    for port in view.input_ports:
        params = ", ".join(["&mut self", "ctx: &mut Context<'_>", "port_num: FwIndexType"] + user_params(port.params))
        unused = unused_tuple(["ctx", "port_num"] + [param.name for param in port.params])
        lines += ["", f"    fn {names.rust_handler(port)}({params}){rust_return_type(port.returns)} {{",
                  f"        let _ = {unused};"]
        if port.returns is not None:
            lines.append(f"        {default_value(port.returns)}")
        lines.append("    }")
        if port.hook:
            lines += ["", f"    fn {names.rust_overflow_hook(port)}({hook_params(params)}) {{", f"        let _ = {unused};", "    }"]
    for port in view.internal_ports:
        params = ", ".join(["&mut self", "ctx: &mut Context<'_>"] + user_params(port.params))
        unused = unused_tuple(["ctx"] + [param.name for param in port.params])
        lines += ["", f"    fn {names.rust_internal_handler(port)}({params}) {{", f"        let _ = {unused};", "    }"]
        if port.hook:
            lines += ["", f"    fn {names.rust_overflow_hook(port)}({hook_params(params)}) {{", f"        let _ = {unused};", "    }"]
    for command in view.commands:
        params = ", ".join(["&mut self", "ctx: &mut Context<'_>"] + user_params(command.params))
        unused = unused_tuple(["ctx"] + [param.name for param in command.params])
        lines += ["", f"    fn {names.rust_cmd_handler(command)}({params}) -> CmdResponse {{",
                  f"        let _ = {unused};", "        CmdResponse::Ok", "    }"]
        if command.hook:
            lines += ["", f"    fn {names.rust_overflow_hook(command)}(ctx: &mut Context<'_>, opcode: FwOpcodeType, cmd_seq: u32) -> CmdResponse {{",
                      "        let _ = (ctx, opcode, cmd_seq);", "        CmdResponse::Busy", "    }"]
    lines += ["}", ""]
    return "\n".join(lines)
