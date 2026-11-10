# `fprime-rust` runtime crate

The Rust-side runtime every generated `<comp>_base.rs` imports. Component authors do not edit it.

| Item | Purpose |
|---|---|
| `CmdResponse` | mirrors `Fw::CmdResponse::T`; returned by command handlers |
| `ParamValid` | mirrors `Fw::ParamValid::T`; returned with every `paramGet_*` |
| `MsgDispatchStatus` | mirrors `Fw::QueuedComponentBase::MsgDispatchStatus`; `Context::last_dispatch()` of queued components |
| `NotThreadSafe` | marker that keeps `Context` `!Send + !Sync` |
| panic hook | installed once per process; forwards message and location to `fprime_rust_assert` (F Prime assertion hook), then aborts |
| `fprime_rust_runtime_marker` | referenced by every generated shim so the runtime objects survive static linking |

The per-component `extern "C"` declarations live in the generated base module, not here. See `../docs/sdd.md`.
