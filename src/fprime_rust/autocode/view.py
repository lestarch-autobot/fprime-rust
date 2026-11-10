"""fprime_rust.autocode.view:

A generator-neutral view of a ``@ fprime-rust`` component: its elements, their names in C++ and Rust
(generated-name table, REQ-026), the Rust and FFI carrier types of every FPP type (type table, REQ-016) and
the rejection of elements this release does not carry over the C ABI (rejected-element table, REQ-017).
"""
from __future__ import annotations

import enum
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Sequence

import fpp

ANNOTATION = "fprime-rust"


class UnsupportedElement(Exception):
    """An FPP element in the rejected-element table was used by a Rust component"""

    def __init__(self, qualified_name: str, reason: str):
        super().__init__(f"unsupported element {qualified_name}: {reason}")
        self.qualified_name = qualified_name


class StringCarrier(enum.Enum):
    """The C++ class F Prime uses for a modeled string in each context, with its default bound constant"""

    PORT = ("Fw::StringBase", "FW_FIXED_LENGTH_STRING_SIZE")
    PORT_RETURN = ("Fw::String", "FW_FIXED_LENGTH_STRING_SIZE")
    COMMAND = ("Fw::CmdStringArg", "FW_CMD_STRING_MAX_SIZE")
    INTERNAL = ("Fw::InternalInterfaceString", "FW_INTERNAL_INTERFACE_STRING_MAX_SIZE")
    PARAMETER = ("Fw::ParamString", "FW_PARAM_STRING_MAX_SIZE")
    EVENT = ("Fw::LogStringArg", "FW_LOG_STRING_MAX_SIZE")
    TELEMETRY = ("Fw::TlmString", "FW_TLM_STRING_MAX_SIZE")


INTEGER_RUST = {
    "U8": "u8", "U16": "u16", "U32": "u32", "U64": "u64",
    "I8": "i8", "I16": "i16", "I32": "i32", "I64": "i64",
}
FLOAT_RUST = {"F32": "f32", "F64": "f64"}


def cpp_name(qualified_name: str) -> str:
    return qualified_name.replace(".", "::")


def flat_name(qualified_name: str) -> str:
    return qualified_name.replace(".", "_")


@dataclass(frozen=True)
class EnumInfo:
    """An FPP enum used by the component"""

    qualified_name: str
    rust_name: str          # Rust identifier (flat, e.g. Fx_Mode); the module re-exports it under its unqualified name
    repr: str               # Rust repr integer type
    cpp_name: str           # C++ class name, e.g. Fx::Mode
    constants: List[tuple]  # (name, value)
    runtime: bool = False   # provided by the fprime_rust runtime crate (Fw.ParamValid, Fw.CmdResponse): no enum block

    def variant_name(self, fpp_constant: str) -> str:
        """Rust variant for an FPP constant: generated enums keep the FPP name, the runtime crate's enums are
        UpperCamel (`INVALID_OPCODE` -> `InvalidOpcode`, `UNINIT` -> `Uninit`)"""
        if not self.runtime:
            return fpp_constant
        return "".join(part[:1].upper() + part[1:].lower() for part in fpp_constant.split("_") if part)


# FPP enums the runtime crate already defines; generating them again would clash with the base module's re-exports
RUNTIME_ENUMS = {"Fw.ParamValid": "ParamValid", "Fw.CmdResponse": "CmdResponse"}


@dataclass(frozen=True)
class TypeInfo:
    """How one FPP type crosses the FFI"""

    kind: str                        # "int", "float", "bool", "string", "enum"
    rust: str                        # Rust type as seen by the user: u32, bool, &str, Mode
    ffi: str                         # FFI carrier type in Rust: u32, u8, (*const u8, usize) -> "str"
    cpp: str                         # C++ type name as F Prime spells it: U32, bool, Fw::StringBase, Fx::Mode
    cpp_value: str                   # C++ spelling when passed by value/const ref in generated signatures
    string_size: Optional[str] = None  # declared `string size` or the carrier's bound constant
    enum: Optional[EnumInfo] = None
    is_primitive: bool = True

    @property
    def string_capacity(self) -> str:
        """Buffer size expression: a `string size N` carrier and an `FW_*_STRING_MAX_SIZE`-bounded carrier both hold
        their size in characters plus the NUL (F Prime `BUFFER_SIZE(size)`)"""
        return f"{self.string_size} + 1"

    def rust_string_capacity(self, where: str) -> str:
        """Rust needs a compile-time array length, which the C++ carrier macros cannot provide"""
        if self.string_size is None or not self.string_size.isdigit():
            raise UnsupportedElement(where, "unsized string read into Rust needs a declared `string size N`")
        return self.string_capacity

    @property
    def by_const_ref(self) -> bool:
        return self.kind in ("string", "enum")


@dataclass(frozen=True)
class Param:
    name: str
    type: TypeInfo
    is_ref: bool = False


@dataclass(frozen=True)
class Port:
    name: str
    kind: str                # "sync", "guarded", "async", "output"
    port_qualified_name: str
    params: List[Param]
    returns: Optional[TypeInfo]
    array_size: int
    hook: bool               # queue full `hook`


@dataclass(frozen=True)
class InternalPort:
    name: str
    params: List[Param]
    hook: bool


@dataclass(frozen=True)
class Command:
    name: str
    kind: str                # "sync", "guarded", "async"
    opcode: int
    params: List[Param]
    hook: bool


@dataclass(frozen=True)
class Event:
    name: str
    severity: str            # ACTIVITY_LO, ACTIVITY_HI, WARNING_LO, WARNING_HI, COMMAND, DIAGNOSTIC, FATAL
    params: List[Param]


@dataclass(frozen=True)
class Channel:
    name: str
    type: TypeInfo


@dataclass(frozen=True)
class Parameter:
    name: str
    id: int
    type: TypeInfo


SEVERITIES = {
    "ActivityLow": "ACTIVITY_LO", "ActivityHigh": "ACTIVITY_HI", "WarningLow": "WARNING_LO",
    "WarningHigh": "WARNING_HI", "Command": "COMMAND", "Diagnostic": "DIAGNOSTIC", "Fatal": "FATAL",
}

GENERAL_KINDS = {"SyncInput": "sync", "GuardedInput": "guarded", "AsyncInput": "async", "Output": "output"}

COMMAND_KINDS = {"Sync": "sync", "Guarded": "guarded", "Async": "async"}


def variant_name(value) -> str:
    """Name of an fpp enum-like value, whether a Python enum member or a variant instance"""
    name = getattr(value, "name", None)
    return name if isinstance(name, str) else type(value).__name__

COMPONENT_KINDS = {"Active": "active", "Queued": "queued", "Passive": "passive"}


def is_annotated(node: fpp.ast.DefComponent) -> bool:
    """Whether a component definition carries ``@ fprime-rust`` (REQ-001)"""
    return any(line.strip() == ANNOTATION for line in node.pre_annotation)


QUEUE_FULL_KEYWORDS = ("assert", "block", "drop", "hook")


def _spec_text(node) -> str:
    """The FPP source text of a specifier, from its span (fpp spans are 0-based, end exclusive)"""
    span = node.span
    lines = Path(str(span.uri)).read_text(encoding="utf-8").splitlines()
    if span.line == span.end_line:
        return lines[span.line][span.column:span.end_column]
    return "\n".join([lines[span.line][span.column:]] + lines[span.line + 1:span.end_line] + [lines[span.end_line][:span.end_column]])


def _queue_full_hook(node) -> bool:
    """Whether a specifier selects the `hook` queue-full behavior

    fprime-fpp-python 4.0.1 exposes `queue_full` on internal port specifiers only; for general ports and
    commands the trailing queue-full keyword is read from the specifier's own source text, which may span lines
    (comments and `@<` annotations are removed per line first).
    """
    queue_full = getattr(node, "queue_full", None)
    if queue_full is not None:
        return variant_name(queue_full) == "Hook"
    if not hasattr(node, "span"):
        return False
    code = " ".join(line.split("#", 1)[0].split("@<", 1)[0] for line in _spec_text(node).splitlines())
    tokens = code.split()
    return bool(tokens) and tokens[-1] == "hook"


@dataclass
class ComponentView:
    """Everything the generators need to know about one Rust component"""

    qualified_name: str
    namespaces: List[str]
    name: str
    kind: str
    include_path: str
    input_ports: List[Port] = field(default_factory=list)
    output_ports: List[Port] = field(default_factory=list)
    internal_ports: List[InternalPort] = field(default_factory=list)
    commands: List[Command] = field(default_factory=list)
    events: List[Event] = field(default_factory=list)
    channels: List[Channel] = field(default_factory=list)
    parameters: List[Parameter] = field(default_factory=list)
    enums: List[EnumInfo] = field(default_factory=list)
    platform_types: dict = field(default_factory=dict)  # FwIndexType etc. -> Rust integer type

    @property
    def flat_name(self) -> str:
        return flat_name(self.qualified_name)

    @property
    def ffi_prefix(self) -> str:
        return f"fprime_rust_{self.flat_name}"

    @property
    def cpp_name(self) -> str:
        return cpp_name(self.qualified_name)

    @property
    def base_class(self) -> str:
        return f"{self.name}ComponentBase"

    @property
    def crate_name(self) -> str:
        return self.flat_name.lower()

    @property
    def base_module(self) -> str:
        return f"{self.name.lower()}_base"

    @property
    def user_module(self) -> str:
        """Module name of the user's `<Comp>.rs` inside the component crate"""
        return self.name.lower()

    @property
    def is_queued_kind(self) -> bool:
        """Active and queued components own a queue"""
        return self.kind in ("active", "queued")

    @property
    def has_queue_drain(self) -> bool:
        """Only a `queued` component drains its queue from its sync/guarded entries"""
        return self.kind == "queued"


class ModelView:
    """Builds ``ComponentView`` objects for the annotated components of an analyzed model"""

    def __init__(self, model: fpp.Model, prefixes: Sequence[Path], working_directory: Optional[Path] = None):
        self.model = model
        self.analysis = model.analysis
        cwd = Path.cwd() if working_directory is None else working_directory
        self.prefixes = [(cwd / prefix).resolve() for prefix in prefixes]
        self._enums: dict = {}

    # -- selection -------------------------------------------------------------------------------------------

    def annotated_components(self) -> List[fpp.Component]:
        """Annotated components defined in the sources (not the imports), in model order"""
        return [
            component
            for component in self.analysis.component_map.values()
            if component.node.in_source and is_annotated(component.node)
        ]

    def views(self) -> List[ComponentView]:
        return [self.component_view(component) for component in self.annotated_components()]

    # -- include paths ---------------------------------------------------------------------------------------

    def include_path(self, symbol, file_name: str) -> str:
        """Include path of a file F Prime generates next to ``symbol``, relative to the closest prefix"""
        directory = Path(symbol.definition.location.uri).resolve().parent
        candidates = sorted(
            (directory.relative_to(prefix) for prefix in self.prefixes if directory.is_relative_to(prefix)),
            key=lambda path: len(path.parents),
        )
        if not candidates:
            raise UnsupportedElement(
                symbol.qualified_name,
                f"defined in {directory}, under none of the build locations {[str(p) for p in self.prefixes]}",
            )
        return file_name if candidates[0] == Path(".") else f"{candidates[0].as_posix()}/{file_name}"

    # -- types -----------------------------------------------------------------------------------------------

    def resolve_type(self, type_name) -> fpp.Type.Variant:
        return self.analysis.type_map[type_name.node_id]

    def enum_rust_name(self, qualified_name: str) -> str:
        """Type-table row `enum E` -> Rust `E`; two enums sharing a simple name cannot both be generated"""
        simple = qualified_name.rsplit(".", 1)[-1]
        for other, info in self._enums.items():
            if info.rust_name == simple and other != qualified_name:
                raise UnsupportedElement(qualified_name, f"enum {other} already generates Rust `{simple}`")
        return simple

    def enum_info(self, enum_type: fpp.Type.Enum) -> EnumInfo:
        symbol = enum_type.def_symbol
        if symbol.qualified_name not in self._enums:
            constants = []
            for constant in enum_type.node.constants:
                # Value.EnumConstant.value is the (name, integer) pair of the constant
                value = self.analysis.value_map[constant.node_id].value
                constants.append((constant.name, int(value[1] if isinstance(value, tuple) else value)))
            runtime_name = RUNTIME_ENUMS.get(symbol.qualified_name)
            self._enums[symbol.qualified_name] = EnumInfo(
                qualified_name=symbol.qualified_name,
                rust_name=runtime_name or self.enum_rust_name(symbol.qualified_name),
                repr=INTEGER_RUST[enum_type.rep_type.name],
                cpp_name=cpp_name(symbol.qualified_name),
                constants=constants,
                runtime=runtime_name is not None,
            )
        return self._enums[symbol.qualified_name]

    def type_info(self, type_: fpp.Type.Variant, owner: str, carrier: StringCarrier) -> TypeInfo:
        """Map an FPP type per the type table; raise ``UnsupportedElement`` for rejected types"""
        underlying = type_.underlying_type
        # fpp-to-cpp spells an alias by its own name (e.g. Fx::Count), the FFI carries the underlying type
        alias = cpp_name(type_.def_symbol.qualified_name) if isinstance(type_, fpp.Type.Alias) else None
        if isinstance(underlying, fpp.Type.PrimitiveInt):
            name = underlying.value.name
            return TypeInfo("int", INTEGER_RUST[name], INTEGER_RUST[name], name, alias or name)
        if isinstance(underlying, fpp.Type.Float):
            name = underlying.value.name
            return TypeInfo("float", FLOAT_RUST[name], FLOAT_RUST[name], name, alias or name)
        if isinstance(underlying, fpp.Type.Boolean):
            return TypeInfo("bool", "bool", "u8", "bool", alias or "bool")
        if isinstance(underlying, fpp.Type.String):
            size = str(underlying.value) if underlying.value is not None else carrier.value[1]
            return TypeInfo("string", "&str", "str", carrier.value[0], carrier.value[0], string_size=size,
                            is_primitive=False)
        if isinstance(underlying, fpp.Type.Enum):
            info = self.enum_info(underlying)
            return TypeInfo("enum", info.rust_name, info.repr, info.cpp_name, alias or info.cpp_name, enum=info,
                            is_primitive=False)
        # struct, array, abstract (REQ-017)
        symbol = type_.def_symbol if type_.def_symbol is not None else underlying.def_symbol
        name = symbol.qualified_name if symbol is not None else repr(type_)
        raise UnsupportedElement(owner, f"type {name} is not carried over the C ABI in this release")

    def params(self, formal_params, owner: str, carrier: StringCarrier) -> List[Param]:
        """`ref` parameters are rejected: a value copied over the C ABI cannot write back to the caller"""
        for param in formal_params:
            if variant_name(param.kind) == "Ref":
                raise UnsupportedElement(f"{owner}.{param.name}", "ref port parameter has no write-back across the C ABI")
        return [
            Param(param.name, self.type_info(self.resolve_type(param.type_name), f"{owner}.{param.name}", carrier))
            for param in formal_params
        ]

    PLATFORM_TYPES = ("FwIndexType", "FwSizeType", "FwOpcodeType", "FwPrmIdType", "FwEnumStoreType", "FwChanIdType",
                      "FwEventIdType")

    def platform_types(self) -> dict:
        """Rust spelling of the F Prime platform integer aliases the generated code uses, from the model"""
        resolved = {}
        for name in self.PLATFORM_TYPES:
            symbol = self.model.lookup(name)
            type_ = self.analysis.type_map[symbol.node_id]
            resolved[name] = INTEGER_RUST[type_.underlying_type.value.name]
        return resolved

    # -- component --------------------------------------------------------------------------------------------

    def component_view(self, component: fpp.Component) -> ComponentView:
        symbol = component.symbol
        qualified = symbol.qualified_name
        self._enums = {}
        view = ComponentView(
            qualified_name=qualified,
            namespaces=self.analysis.get_enclosing_names(symbol),
            name=symbol.unqualified_name,
            kind=COMPONENT_KINDS[variant_name(component.node.kind)],
            include_path=self.include_path(symbol, f"{symbol.unqualified_name}ComponentAc.hpp"),
        )
        if component.has_data_products or component.container_map or component.record_map:
            raise UnsupportedElement(qualified, "data products take Fw::DpContainer")
        if component.state_machine_instance_map:
            name = next(iter(component.state_machine_instance_map))
            raise UnsupportedElement(f"{qualified}.{name}", "state machine instances take a state-machine id and signal")
        for name, instance in component.port_map.items():
            owner = f"{qualified}.{name}"
            if isinstance(instance, fpp.PortInstance.General):
                if isinstance(instance.type, fpp.PortInstanceType.Serial):
                    raise UnsupportedElement(owner, "serial ports take a serialization buffer")
                definition = instance.type.definition
                port_symbol = self.analysis.symbol_map[definition.node_id]
                kind = GENERAL_KINDS[variant_name(instance.kind)]
                carrier = StringCarrier.PORT
                params = self.params(definition.params, owner, carrier)
                returns = (
                    self.type_info(self.resolve_type(definition.return_type), owner, StringCarrier.PORT_RETURN)
                    if definition.return_type is not None else None
                )
                port = Port(name, kind, port_symbol.qualified_name, params, returns, instance.array_size,
                            _queue_full_hook(instance.node))
                (view.output_ports if kind == "output" else view.input_ports).append(port)
            elif isinstance(instance, fpp.PortInstance.Internal):
                view.internal_ports.append(InternalPort(
                    name, self.params(instance.node.params, owner, StringCarrier.INTERNAL), _queue_full_hook(instance.node)))
            elif isinstance(instance, fpp.PortInstance.Special):
                special = instance.special_kind
                if "Product" in str(special):
                    raise UnsupportedElement(owner, "data product ports take Fw::DpContainer")
        for opcode, command in component.command_map.items():
            if not isinstance(command, fpp.Command.NonParam):
                continue
            owner = f"{qualified}.{command.name}"
            view.commands.append(Command(
                command.name, COMMAND_KINDS[variant_name(command.kind)], opcode,
                self.params(command.node.params, owner, StringCarrier.COMMAND), _queue_full_hook(command.node)))
        for event in component.event_map.values():
            owner = f"{qualified}.{event.name}"
            view.events.append(Event(event.name, SEVERITIES[variant_name(event.node.severity)],
                                     self.params(event.node.params, owner, StringCarrier.EVENT)))
        for channel in component.tlm_channel_map.values():
            owner = f"{qualified}.{channel.name}"
            view.channels.append(Channel(channel.name, self.type_info(channel.channel_type, owner, StringCarrier.TELEMETRY)))
        for identifier, parameter in component.param_map.items():
            owner = f"{qualified}.{parameter.name}"
            view.parameters.append(Parameter(parameter.name, identifier,
                                             self.type_info(parameter.param_type, owner, StringCarrier.PARAMETER)))
        view.enums = sorted(self._enums.values(), key=lambda info: info.qualified_name)
        view.platform_types = self.platform_types()
        return view
