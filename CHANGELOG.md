# Changelog

All notable changes to `fprime-rust` will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - Unreleased

### Added

- Autocoder on `fpp.analyze` over the module closure from `fpp-cache/stdout.txt`; generated C++ shim, Rust base
  module and user template per the SDD name table; one Cargo workspace and one static archive per deployment
  executable (`fprime-rust-ac crate`); runtime crate with `CmdResponse`, `ParamValid`, `MsgDispatchStatus` and the
  panic-to-`FW_ASSERT` bridge; `include(FprimeRust)` CMake integration; component cookiecutter; pytest, cargo and
  F Prime C++ fixture unit tests.

### Changed

- Generated `Context` helper methods now mirror the standard F Prime C++
  `ComponentBase` API names exactly: `tlmWrite_<Channel>`,
  `log_<SEVERITY>_<Event>`, `paramGet_<Param>`, and `cmdResponse_out`.
  Previously the generator emitted `tlm_write_*`, `log_*` (severity
  stripped), `param_*`, and `command_response`, which forced Rust authors
  to learn a parallel vocabulary.  Generated modules now carry a
  `#![allow(non_snake_case)]` so Rust's snake_case lint stays quiet.

### Added

- Initial public scaffolding for a Rust autocoder for F Prime.
- `fprime-rust-ac` CLI with `bindings` and `crate` subcommands.
- C++ shim generator (`<Component>.{hpp,cpp}`).
- Rust base/template generator (`<component>_base.rs`, `<Component>.template.rs`).
- Cargo workspace generator (`Cargo.toml`, `lib.rs`, `rust-toolchain.toml`).
- `fprime-rust` runtime crate exposing `CmdResponse`, `ParamValid`, and
  `Context`.
- CMake autocoder hook (`cmake/autocoder/fprime_rust.cmake`).
- CMake target hook (`cmake/target/fprime_rust.cmake`).
- `RustExample` reference component (in
  [`fprime-rust-reference`](https://github.com/JPL-Devin/fprime-rust-reference))
  demonstrating a command, an event, a telemetry channel, and a parameter.
- Software design description (`docs/design.md`) and architecture overview
  (`docs/architecture.md`).
- `pytest` test suite covering the FPP parser, the generators, and the CLI.
