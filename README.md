# fprime-rust: Rust components for F Prime

`fprime-rust` is an [F Prime](https://fprime.jpl.nasa.gov/) autocoder plugin that lets a component be
implemented in Rust while the FPP model, the C++ component base classes, the topology, the dictionary and the
GDS stay exactly as they are. It follows the shape of
[`fprime-python`](https://github.com/fprime-community/fprime-python). The design is
[`docs/sdd.md`](docs/sdd.md); this README is the operator's view of it.

## How it works

1. Annotate a component `@ fprime-rust` in its `.fpp` file. FPP is authoritative: ports, commands, events,
   telemetry, parameters and their types all come from the model.
2. `fprime-rust-ac bindings` runs as an F Prime autocoder on each module build directory. It loads the module's
   complete FPP closure from `fpp-cache/stdout.txt` with `fpp.analyze` (no JSON model is written or read) and,
   for every annotated component, generates:
   - `<Comp>.hpp` / `<Comp>.cpp` — the C++ shim deriving from the FPP-generated `<Comp>ComponentBase`; every
     handler forwards to Rust through `extern "C"` functions, under the instance mutex rule of the SDD
     (queued components drain their queue in every sync/guarded entry and never re-lock in async entries);
   - `<comp>_base.rs` — the Rust base module: the `Component` trait with one method per handler, and a
     `Context` (not `Send`/`Sync`) exposing `log_*`, `tlmWrite_*`, `paramGet_*`, output-port and internal-port
     calls with the same names as the C++ base class;
   - `<Comp>.template.rs` — a user template, written into the module build directory. `<Comp>.rs` is seeded
     from it when absent and is the only file the component author edits.
3. `fprime-rust-ac crate` runs once per deployment executable and emits one Cargo workspace under
   `<build>/fprime_rust/<EXECUTABLE>/`: one rlib member per Rust component and a `staticlib` root. `cargo build`
   produces the single `libfprime_rust_<EXECUTABLE>.a` that is linked into the executable, after the shim
   objects, together with the C++ runtime (`FprimeRust/`) that bridges Rust panics to `FW_ASSERT`.

Supported FPP types across the FFI: integers, floats, `bool`, enums, strings (borrowed into Rust as `&str`,
bounded by the carrier capacity, truncated at an interior NUL, invalid UTF-8 replaced by U+FFFD) and aliases of
these. Structs, arrays, `Fw.Buffer`/`Fw.Com` arguments, serial ports, state machines and data products are
rejected with a clear `unsupported element <qualified name>` error at generation time, as are unsized strings
read into Rust (parameters and port returns need `string size N`).

## Repository layout

```
cmake/
  FprimeRust.cmake            # include(FprimeRust): registers the autocoder, the target and the runtime
  autocoder/fprime_rust.cmake # per-module autocoder: fprime-rust-ac bindings
  target/fprime_rust.cmake    # per-executable target: fprime-rust-ac crate + cargo build + link
FprimeRust/                   # C++ runtime: panic/assert bridge, string assignment, runtime marker
runtime/                      # Rust runtime crate: CmdResponse, ParamValid, MsgDispatchStatus, panic hook
src/fprime_rust/autocode/     # the generator (model.py, view.py, names.py, cpp_shim.py, rust_base.py, ...)
cookiecutters/component/      # fprime-util new --component template for a Rust component
tests/                        # pytest (generator) and tests/project (F Prime fixture project with C++ UTs)
docs/sdd.md                   # the design
```

## Setup

```bash
python3 -m venv fprime-venv && source fprime-venv/bin/activate
pip install -r lib/fprime/requirements.txt
pip install -e lib/fprime-rust            # provides fprime-rust-ac; pins fprime-fpp-python==4.0.1
curl https://sh.rustup.rs -sSf | sh       # stable toolchain; cargo must be on PATH
```

In the project `CMakeLists.txt`, after `include("${FPRIME_FRAMEWORK_PATH}/cmake/FPrime.cmake")`:

```cmake
include(FprimeRust)
```

and list `lib/fprime-rust` under `library_locations` in `settings.ini`. A Rust component module registers its
sources as usual:

```cmake
register_fprime_module(
    AUTOCODER_INPUTS "${CMAKE_CURRENT_LIST_DIR}/RustCounter.fpp"
    SOURCES          "${CMAKE_CURRENT_LIST_DIR}/RustCounter.rs"
)
```

`fprime-util generate && fprime-util build` then builds the Rust code with the deployment. Unit tests of a Rust
component are ordinary F Prime GTest unit tests over the generated shim (`fprime-util check`).

## Writing a component

```rust
use crate::rustcounter_base::*;

pub struct RustCounter { counter: u32 }

impl Component for RustCounter {
    fn new() -> Self { RustCounter { counter: 0 } }

    fn BUMP_cmd_handler(&mut self, ctx: &mut Context<'_>, amount: u32) -> CmdResponse {
        let (threshold, _valid) = ctx.paramGet_THRESHOLD();
        self.counter = self.counter.saturating_add(amount).min(threshold);
        ctx.log_ACTIVITY_LO_Bumped(self.counter);
        CmdResponse::Ok
    }
}
```

`fprime-util new --component` with this repository's cookiecutter (`cookiecutters/component`) creates the
module, the annotated `.fpp`, the `.rs` and an SDD skeleton. The reference deployment lives in
[`fprime-rust-reference`](https://github.com/lestarch-autobot/fprime-rust-reference).

## Testing

```bash
pytest                                   # generator tests (pip install -e ".[test]")
(cd runtime && cargo test)               # runtime conversions and the panic bridge
(cd tests/project && fprime-util generate --ut && fprime-util check --all)   # C++ fixture unit tests over the shim
FPRIME_RUST_FIXTURE_BUILD=tests/project/build-fprime-automatic-native-ut pytest tests/test_build.py
```

## License

Apache 2.0, same as F Prime.
