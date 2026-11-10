"""fprime_rust.autocode.names:

The generated-name table (REQ-FprimeRust-026): for a component ``Ns.Comp`` and element ``X`` the C++ shim
member, the FFI symbol ``fprime_rust_Ns_Comp_<suffix>`` and the Rust name of every element kind.
"""
from __future__ import annotations

from .view import Channel, Command, ComponentView, Event, InternalPort, Parameter, Port


def ffi(view: ComponentView, suffix: str) -> str:
    return f"{view.ffi_prefix}_{suffix}"


# -- Rust -> C++ entries exported by the base module (shim calls these) --------------------------------------

def handler(view: ComponentView, port: Port) -> str:
    return ffi(view, f"{port.name}_handler")


def internal_handler(view: ComponentView, port: InternalPort) -> str:
    return ffi(view, f"{port.name}_internal_handler")


def overflow_hook(view: ComponentView, element) -> str:
    return ffi(view, f"{element.name}_overflow_hook")


def cmd_handler(view: ComponentView, command: Command) -> str:
    return ffi(view, f"{command.name}_cmd_handler")


def parameter_updated(view: ComponentView) -> str:
    return ffi(view, "parameter_updated")


def lifecycle(view: ComponentView, step: str) -> str:
    """``new`` / ``init`` / ``drop``"""
    return ffi(view, step)


# -- C++ -> Rust helpers exported by the shim (Context calls these) ------------------------------------------

def out(view: ComponentView, port: Port) -> str:
    return ffi(view, f"{port.name}_out")


def internal_invoke(view: ComponentView, port: InternalPort) -> str:
    return ffi(view, f"{port.name}_internal_invoke")


def log(view: ComponentView, event: Event) -> str:
    return ffi(view, f"log_{event.severity}_{event.name}")


def tlm_write(view: ComponentView, channel: Channel) -> str:
    return ffi(view, f"tlmWrite_{channel.name}")


def param_get(view: ComponentView, parameter: Parameter) -> str:
    return ffi(view, f"paramGet_{parameter.name}")


def num_msgs_dropped(view: ComponentView) -> str:
    return ffi(view, "num_msgs_dropped")


# -- C++ shim member names (what the autocoded base declares) ------------------------------------------------

def cpp_handler(port: Port) -> str:
    return f"{port.name}_handler"


def cpp_out(port: Port) -> str:
    return f"{port.name}_out"


def cpp_internal_handler(port: InternalPort) -> str:
    return f"{port.name}_internalInterfaceHandler"


def cpp_internal_invoke(port: InternalPort) -> str:
    return f"{port.name}_internalInterfaceInvoke"


def cpp_overflow_hook(element) -> str:
    return f"{element.name}_cmdOverflowHook" if isinstance(element, Command) else f"{element.name}_overflowHook"


def cpp_cmd_handler(command: Command) -> str:
    return f"{command.name}_cmdHandler"


def cpp_log(event: Event) -> str:
    return f"log_{event.severity}_{event.name}"


def cpp_tlm_write(channel: Channel) -> str:
    return f"tlmWrite_{channel.name}"


def cpp_param_get(parameter: Parameter) -> str:
    return f"paramGet_{parameter.name}"


# -- Rust names (trait methods and Context helpers) ----------------------------------------------------------

def rust_handler(port: Port) -> str:
    return f"{port.name}_handler"


def rust_out(port: Port) -> str:
    return f"{port.name}_out"


def rust_internal_handler(port: InternalPort) -> str:
    return f"{port.name}_internal_handler"


def rust_internal_invoke(port: InternalPort) -> str:
    return f"{port.name}_internal_invoke"


def rust_overflow_hook(element) -> str:
    return f"{element.name}_overflow_hook"


def rust_cmd_handler(command: Command) -> str:
    return f"{command.name}_cmd_handler"


def rust_log(event: Event) -> str:
    return f"log_{event.severity}_{event.name}"


def rust_tlm_write(channel: Channel) -> str:
    return f"tlmWrite_{channel.name}"


def rust_param_get(parameter: Parameter) -> str:
    return f"paramGet_{parameter.name}"
