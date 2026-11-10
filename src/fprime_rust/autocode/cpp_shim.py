"""fprime_rust.autocode.cpp_shim:

Generates ``<Comp>.hpp`` / ``<Comp>.cpp``: the F Prime component (``final``, derives the autocoded base) that
forwards every handler over the FFI to Rust and exports the ``extern "C"`` helpers the Rust ``Context`` calls.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

from fprime_cpp_codegen import Body, CppDocBuilder, Output
from fprime_cpp_codegen.doc import Param as CgParam, Type

from . import names
from .view import Command, ComponentView, InternalPort, Param, Port, TypeInfo

CPP_FFI = {
    "u8": "U8", "u16": "U16", "u32": "U32", "u64": "U64",
    "i8": "I8", "i16": "I16", "i32": "I32", "i64": "I64", "f32": "F32", "f64": "F64",
}

def ffi_type(type_: TypeInfo) -> str:
    """C++ spelling of the FFI carrier of a non-string type"""
    return CPP_FFI[type_.ffi]


def string_buffer_size(type_: TypeInfo) -> str:
    """Size expression of the local carrier buffer for an outgoing string"""
    return type_.string_capacity


# -- signature pieces ----------------------------------------------------------------------------------------

def cpp_param(param: Param, context: str) -> str:
    """One parameter as the autocoded base declares it; ``context`` is port/cmd/internal/event/tlm"""
    type_ = param.type
    if type_.kind == "string":
        if context == "port":
            return f"{'' if param.is_ref else 'const '}Fw::StringBase& {param.name}"
        return f"const {type_.cpp_value}& {param.name}"
    if type_.kind == "enum":
        return f"{'' if param.is_ref else 'const '}{type_.cpp_value}& {param.name}"
    return f"{type_.cpp_value}{'&' if param.is_ref else ''} {param.name}"


def cpp_params(params: List[Param], context: str, leading: List[str]) -> str:
    return ", ".join(leading + [cpp_param(param, context) for param in params])


def ffi_params(params: List[Param]) -> List[str]:
    """FFI carrier parameters (C++ spelling) for a parameter list"""
    out = []
    for param in params:
        if param.type.kind == "string":
            out += [f"const CHAR* {param.name}_ptr", f"FwSizeType {param.name}_len"]
        else:
            out.append(f"{ffi_type(param.type)} {param.name}")
    return out


def to_ffi_args(params: List[Param]) -> List[str]:
    """Convert autocoded-base values into FFI carriers"""
    out = []
    for param in params:
        type_ = param.type
        if type_.kind == "string":
            out += [f"{param.name}.toChar()", f"{param.name}.length()"]
        elif type_.kind == "bool":
            out.append(f"static_cast<U8>({param.name} ? 1 : 0)")
        elif type_.kind == "enum":
            out.append(f"static_cast<{ffi_type(type_)}>({param.name}.e)")
        else:
            out.append(param.name)
    return out


def from_ffi_locals(params: List[Param]) -> Tuple[List[str], List[str]]:
    """Statements rebuilding C++ values from FFI carriers, and the argument expressions to pass on"""
    statements, args = [], []
    for param in params:
        type_ = param.type
        name = param.name
        if type_.kind == "string":
            statements += [
                f"CHAR {name}_buf[{string_buffer_size(type_)}];",
                f"Fw::ExternalString {name}({name}_buf, sizeof({name}_buf));",
                f"(void)FprimeRust::copyBytes({name}_buf, sizeof({name}_buf), {name}_ptr, {name}_len);",
            ]
            args.append(name)
        elif type_.kind == "bool":
            args.append(f"({name} != 0)")
        elif type_.kind == "enum":
            args.append(f"{type_.cpp_value}(static_cast<{type_.cpp}::T>({name}))")
        else:
            args.append(name)
    return statements, args


def return_ffi_params(returns: Optional[TypeInfo]) -> List[str]:
    if returns is None:
        return []
    if returns.kind == "string":
        return ["void* result"]
    return [f"{ffi_type(returns)}* result"]


def helper_return_params(returns: Optional[TypeInfo]) -> List[str]:
    """Result parameters of a shim helper: strings are copied out into a Rust-provided buffer"""
    if returns is None:
        return []
    if returns.kind == "string":
        return ["CHAR* buffer", "FwSizeType capacity", "FwSizeType* length"]
    return [f"{ffi_type(returns)}* result"]


def return_from_ffi(returns: TypeInfo, value: str) -> str:
    """Expression converting an FFI result carrier back into the base's return type"""
    if returns.kind == "bool":
        return f"({value} != 0)"
    if returns.kind == "enum":
        return f"{returns.cpp_value}(static_cast<{returns.cpp}::T>({value}))"
    return value


def return_to_ffi(returns: TypeInfo, call: str) -> str:
    """Statement storing a base call's return value into ``*result``"""
    if returns.kind == "string":
        return f"FprimeRust::assignString(*static_cast<Fw::StringBase*>(result), {call}.toChar(), {call}.length());"
    if returns.kind == "bool":
        return f"*result = static_cast<U8>({call} ? 1 : 0);"
    if returns.kind == "enum":
        return f"*result = static_cast<{ffi_type(returns)}>({call}.e);"
    return f"*result = static_cast<{ffi_type(returns)}>({call});"


# -- policy --------------------------------------------------------------------------------------------------

def takes_lock(view: ComponentView, entry_kind: str) -> bool:
    """Mutex rule: overflow hooks never lock (they never reach the implementation); queued components take no lock on
    async-port, async-command and internal-port entries"""
    if entry_kind in ("hook", "internal_hook"):
        return False
    if view.kind == "queued" and entry_kind in ("async", "internal"):
        return False
    return True


def drains(view: ComponentView, entry_kind: str) -> bool:
    """Queued components drain their queue in every sync/guarded entry before entering Rust"""
    return view.kind == "queued" and entry_kind in ("sync", "guarded")


# -- rust-side entry declarations (what the shim calls) -------------------------------------------------------

def rust_entry_decls(view: ComponentView) -> List[str]:
    decls = [
        f"void* {names.lifecycle(view, 'new')}();",
        f"void {names.lifecycle(view, 'drop')}(void* fprImpl);",
        f"void {names.lifecycle(view, 'init')}(void* fprImpl, FprimeRustContext* fprCtx);",
        f"void {names.parameter_updated(view)}(void* fprImpl, FprimeRustContext* fprCtx, FwPrmIdType id);",
    ]
    for port in view.input_ports:
        params = ["void* fprImpl", "FprimeRustContext* fprCtx", "FwIndexType portNum"] + ffi_params(port.params) \
            + return_ffi_params(port.returns)
        decls.append(f"void {names.handler(view, port)}({', '.join(params)});")
        if port.hook:
            params = ["FprimeRustContext* fprCtx", "FwIndexType portNum"] + ffi_params(port.params)
            decls.append(f"void {names.overflow_hook(view, port)}({', '.join(params)});")
    for port in view.internal_ports:
        params = ["void* fprImpl", "FprimeRustContext* fprCtx"] + ffi_params(port.params)
        decls.append(f"void {names.internal_handler(view, port)}({', '.join(params)});")
        if port.hook:
            decls.append(f"void {names.overflow_hook(view, port)}({', '.join(params[1:])});")
    for command in view.commands:
        params = ["void* fprImpl", "FprimeRustContext* fprCtx"] + ffi_params(command.params)
        decls.append(f"U32 {names.cmd_handler(view, command)}({', '.join(params)});")
        if command.hook:
            decls.append(f"U32 {names.overflow_hook(view, command)}(FprimeRustContext* fprCtx, FwOpcodeType opCode, U32 cmdSeq);")
    return decls


# -- shim-side helper declarations (what Rust calls) -----------------------------------------------------------

def helper_signatures(view: ComponentView) -> List[Tuple[str, str, List[str]]]:
    """(return type, name, params) of every helper the shim exports"""
    helpers = []
    for port in view.output_ports:
        params = ["void* component", "FwIndexType fprPortNum"] + ffi_params(port.params) + helper_return_params(port.returns)
        helpers.append(("void", names.out(view, port), params))
    for port in view.internal_ports:
        helpers.append(("void", names.internal_invoke(view, port), ["void* component"] + ffi_params(port.params)))
    for event in view.events:
        helpers.append(("void", names.log(view, event), ["void* component"] + ffi_params(event.params)))
    for channel in view.channels:
        helpers.append(("void", names.tlm_write(view, channel), ["void* component"] + ffi_params([Param("value", channel.type)])))
    for parameter in view.parameters:
        if parameter.type.kind == "string":
            params = ["void* component", "CHAR* buffer", "FwSizeType capacity", "FwSizeType* length"]
        else:
            params = ["void* component", f"{ffi_type(parameter.type)}* value"]
        helpers.append(("U8", names.param_get(view, parameter), params))
    if view.is_queued_kind:
        helpers.append(("U64", names.num_msgs_dropped(view), ["void* component"]))
    return helpers


# -- header ----------------------------------------------------------------------------------------------------

def _body(statements: List[str]) -> Body:
    """A `fprime_cpp_codegen` body from generator statements (one statement per line, no outer indentation)"""
    body = Body()
    for statement in statements:
        body.line(statement.strip())
    return body


def _params(signature: List[str]) -> List[Tuple[str, str]]:
    """`type name` strings as (type, name) pairs for `fprime_cpp_codegen`"""
    out = []
    for item in signature:
        type_, _, name = item.rpartition(" ")
        out.append((type_, name))
    return out


def _handler_declarations(view: ComponentView):
    """(name, return type, parameter strings, entry kind, body statements) of every base override the shim defines"""
    cls_ = view.name
    for port in view.input_ports:
        ret = port.returns.cpp_value if port.returns else "void"
        params = ["FwIndexType portNum"] + [cpp_param(param, "port") for param in port.params]
        args = ["this->m_impl", "&fprContext", "portNum"] + to_ffi_args(port.params)
        body = _entry_prologue(view, port.kind)
        if port.returns is None:
            body.append(f"{names.handler(view, port)}({', '.join(args)});")
        elif port.returns.kind == "string":
            body += ["Fw::String fprResult;", f"{names.handler(view, port)}({', '.join(args + ['&fprResult'])});", "return fprResult;"]
        else:
            body += [f"{ffi_type(port.returns)} fprResult = 0;", f"{names.handler(view, port)}({', '.join(args + ['&fprResult'])});",
                     f"return {return_from_ffi(port.returns, 'fprResult')};"]
        yield names.cpp_handler(port), ret, params, body
        if port.hook:
            body = _entry_prologue(view, "hook") + [f"{names.overflow_hook(view, port)}({', '.join(args[1:])});"]
            yield names.cpp_overflow_hook(port), "void", params, body
    for port in view.internal_ports:
        params = [cpp_param(param, "internal") for param in port.params]
        args = ["this->m_impl", "&fprContext"] + to_ffi_args(port.params)
        yield names.cpp_internal_handler(port), "void", params, _entry_prologue(view, "internal") + [
            f"{names.internal_handler(view, port)}({', '.join(args)});"]
        if port.hook:
            yield names.cpp_overflow_hook(port), "void", params, _entry_prologue(view, "internal_hook") + [
                f"{names.overflow_hook(view, port)}({', '.join(args[1:])});"]
    for command in view.commands:
        params = ["FwOpcodeType opCode", "U32 cmdSeq"] + [cpp_param(param, "cmd") for param in command.params]
        args = ["this->m_impl", "&fprContext"] + to_ffi_args(command.params)
        respond = "this->cmdResponse_out(opCode, cmdSeq, Fw::CmdResponse(static_cast<Fw::CmdResponse::T>(fprResponse)));"
        yield names.cpp_cmd_handler(command), "void", params, _entry_prologue(view, command.kind) + [
            f"const U32 fprResponse = {names.cmd_handler(view, command)}({', '.join(args)});", respond]
        if command.hook:
            yield names.cpp_overflow_hook(command), "void", ["FwOpcodeType opCode", "U32 cmdSeq"], _entry_prologue(view, "hook") + [
                f"const U32 fprResponse = {names.overflow_hook(view, command)}(&fprContext, opCode, cmdSeq);", respond]
    if view.parameters:
        yield "parameterUpdated", "void", ["FwPrmIdType id"], _entry_prologue(view, "parameter") + [
            f"{names.parameter_updated(view)}(this->m_impl, &fprContext, id);"]


def build_document(view: ComponentView, model_name: str) -> CppDocBuilder:
    """The shim's header and source as one `fprime_cpp_codegen` document (Captain ruling R5: the C++ text is emitted
    through fprime-cpp-codegen, as fprime-python's component generator does)"""
    cls = view.name
    doc = CppDocBuilder(cls, description=f"F Prime shim of `{view.qualified_name}` (model {model_name}); do not edit",
                        include_guard=f"{view.flat_name}_SHIM_HPP", tool_name="fprime-rust-ac", strict=True)
    doc.include(view.include_path, "FprimeRust/FprimeRust.hpp")
    prefix = view.include_path.rsplit("/", 1)[0] + "/" if "/" in view.include_path else ""
    doc.include(f"{prefix}{cls}.hpp", "Fw/Types/ExternalString.hpp", "Fw/Types/String.hpp", output=Output.CPP)
    helpers = helper_signatures(view)
    doc.lines("\n".join(['extern "C" {'] + [f"{ret} {name}({', '.join(params)});" for ret, name, params in helpers] + ["}"]))
    doc.lines("\n".join(["// Entry points exported by the Rust base module", 'extern "C" {'] + rust_entry_decls(view) + ["}"]),
              output=Output.CPP)
    scope = doc.namespace(*view.namespaces) if view.namespaces else doc
    with scope.class_(cls, extends=f"public {view.base_class}", final=True,
                      comment=f"F Prime shim of `{view.qualified_name}`: forwards the autocoded base's handlers to the Rust implementation") as c:
        with c.public():
            c.constructor(params=[("const char* const", "compName")],
                          initializers=[f"{view.base_class}(compName)", f"m_impl({names.lifecycle(view, 'new')}())", "m_mutex()"],
                          explicit=True, comment="Construct the component and its Rust implementation (`Implementation::new`)",
                          body=_body(["// Reference the Rust runtime marker: one Rust runtime per executable (REQ-FprimeRust-020)",
                                      "static_cast<void>(fprime_rust_runtime_marker());"]))
            c.destructor(comment="Drop the Rust implementation",
                         body=_body([f"{names.lifecycle(view, 'drop')}(this->m_impl);", "this->m_impl = nullptr;"]))
            c.constructor(params=[(f"const {cls}&", "")], deleted=True)
            c.function("operator=", ret=f"{cls}&", params=[(f"const {cls}&", "")], deleted=True)
            init_params = [CgParam(Type("FwSizeType"), "queueDepth")] if view.is_queued_kind else []
            init_params.append(CgParam(Type("FwEnumStoreType"), "instance", default="0"))
            base_init = f"{view.base_class}::init({'queueDepth, ' if view.is_queued_kind else ''}instance);"
            c.function("init", params=init_params, comment="Initialize the base, then the Rust implementation (`init`)",
                       body=_body([base_init, "FprimeRust::Lock lock(this->m_mutex);", "FprimeRustContext fprContext = {this, 0};",
                                   f"{names.lifecycle(view, 'init')}(this->m_impl, &fprContext);"]))
        with c.private():
            for name, ret, params, body in _handler_declarations(view):
                c.function(name, ret=ret, params=_params(params), override=True, body=_body(body))
            c.lines("//! The Rust `Context` helpers reach the protected base through these")
            for ret, name, params in helpers:
                c.friend(f"{ret} ::{name}({', '.join(params)})")
            c.var("void*", "m_impl", comment="Opaque Rust `Implementation` (Box)")
            c.var("Os::Mutex", "m_mutex", comment="Non-recursive instance mutex (mutex rule)")
    doc.lines("\n".join(_helper_definitions(view)), output=Output.CPP)
    return doc


def generate_hpp(view: ComponentView, model_name: str) -> str:
    return build_document(view, model_name).files()[f"{view.name}.hpp"]


# -- source ----------------------------------------------------------------------------------------------------

def _entry_prologue(view: ComponentView, entry_kind: str) -> List[str]:
    lines = []
    if takes_lock(view, entry_kind):
        lines.append("FprimeRust::Lock lock(this->m_mutex);")
    lines.append("FprimeRustContext fprContext = {this, 0};")
    if drains(view, entry_kind):
        lines.append("fprContext.last_dispatch = static_cast<U32>(this->dispatchAvailableMessages());")
    return lines


def _helper_definitions(view: ComponentView) -> List[str]:
    cls = view.cpp_name
    lines: List[str] = ['extern "C" {', ""]
    self_line = f"    {cls}* const fprSelf = static_cast<{cls}*>(component);"
    for port in view.output_ports:
        params = ["void* component", "FwIndexType fprPortNum"] + ffi_params(port.params) + helper_return_params(port.returns)
        lines.append(f"void {names.out(view, port)}({', '.join(params)}) {{")
        lines.append(self_line)
        statements, args = from_ffi_locals(port.params)
        lines += [f"    {statement}" for statement in statements]
        call = f"fprSelf->{names.cpp_out(port)}({', '.join(['fprPortNum'] + args)})"
        if port.returns is None:
            lines.append(f"    {call};")
        elif port.returns.kind == "string":
            lines += [f"    const Fw::String returned = {call};",
                      "    *length = FprimeRust::copyBytes(buffer, capacity, returned.toChar(), returned.length());"]
        else:
            lines.append(f"    {return_to_ffi(port.returns, call)}")
        lines += ["}", ""]
    for port in view.internal_ports:
        params = ["void* component"] + ffi_params(port.params)
        lines.append(f"void {names.internal_invoke(view, port)}({', '.join(params)}) {{")
        lines.append(self_line)
        statements, args = from_ffi_locals(port.params)
        lines += [f"    {statement}" for statement in statements]
        lines += [f"    fprSelf->{names.cpp_internal_invoke(port)}({', '.join(args)});", "}", ""]
    for event in view.events:
        params = ["void* component"] + ffi_params(event.params)
        lines.append(f"void {names.log(view, event)}({', '.join(params)}) {{")
        lines.append(self_line)
        statements, args = from_ffi_locals(event.params)
        lines += [f"    {statement}" for statement in statements]
        lines += [f"    fprSelf->{names.cpp_log(event)}({', '.join(args)});", "}", ""]
    for channel in view.channels:
        value = Param("value", channel.type)
        lines.append(f"void {names.tlm_write(view, channel)}({', '.join(['void* component'] + ffi_params([value]))}) {{")
        lines.append(self_line)
        statements, args = from_ffi_locals([value])
        lines += [f"    {statement}" for statement in statements]
        lines += [f"    fprSelf->{names.cpp_tlm_write(channel)}({args[0]});", "}", ""]
    for parameter in view.parameters:
        type_ = parameter.type
        if type_.kind == "string":
            lines.append(f"U8 {names.param_get(view, parameter)}(void* component, CHAR* buffer, FwSizeType capacity, FwSizeType* length) {{")
            lines += [self_line, "    Fw::ParamValid valid;",
                      f"    const Fw::ParamString value = fprSelf->{names.cpp_param_get(parameter)}(valid);",
                      "    *length = FprimeRust::copyBytes(buffer, capacity, value.toChar(), value.length());"]
        else:
            lines.append(f"U8 {names.param_get(view, parameter)}(void* component, {ffi_type(type_)}* value) {{")
            lines += [self_line, "    Fw::ParamValid valid;"]
            call = f"fprSelf->{names.cpp_param_get(parameter)}(valid)"
            if type_.kind == "bool":
                lines.append(f"    *value = static_cast<U8>({call} ? 1 : 0);")
            elif type_.kind == "enum":
                lines.append(f"    *value = static_cast<{ffi_type(type_)}>({call}.e);")
            else:
                lines.append(f"    *value = static_cast<{ffi_type(type_)}>({call});")
        lines += ["    return static_cast<U8>(valid.e);", "}", ""]
    if view.is_queued_kind:
        lines += [f"U64 {names.num_msgs_dropped(view)}(void* component) {{", self_line,
                  "    return static_cast<U64>(fprSelf->getNumMsgsDropped());", "}", ""]
    lines.append('}  // extern "C"')
    return lines


def generate_cpp(view: ComponentView, model_name: str) -> str:
    return build_document(view, model_name).files()[f"{view.name}.cpp"]
