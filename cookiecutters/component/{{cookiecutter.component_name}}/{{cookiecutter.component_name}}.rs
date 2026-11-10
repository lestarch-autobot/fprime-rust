//! `{{cookiecutter.component_namespace}}.{{cookiecutter.component_name}}`: {{cookiecutter.component_short_description}}
//!
//! Each build writes `{{cookiecutter.component_name}}.template.rs` into the module build directory with a stub for every handler
//! in the model. Copy the stubs of newly modeled handlers from there into this file.
use crate::{{cookiecutter.component_name|lower}}_base::*;
{% if cookiecutter.component_kind == "queued" %}
// NOTE (queued component): every sync/guarded input of a Rust queued component drains the queue before
// its handler runs, on the caller's thread. Give the component exactly one sync/guarded input (its `run`)
// unless that is intended, and declare the other inputs `async`. Rust-to-Rust synchronous edges are lock
// edges and must form a DAG: break cycles with an `async` port.
{% endif %}
#[derive(Default)]
pub struct {{cookiecutter.component_name}} {
    hello_count: u32,
}

impl Component for {{cookiecutter.component_name}} {
    fn new() -> Self {
        Self::default()
    }
{% if cookiecutter.component_kind == "queued" %}
    fn run_handler(&mut self, _ctx: &mut Context<'_>, _port_num: FwIndexType, _context: u32) {
        // the queue was drained before this handler was entered
    }
{% endif %}
    fn HELLO_cmd_handler(&mut self, ctx: &mut Context<'_>, greeting: &str) -> CmdResponse {
        self.hello_count += 1;
        ctx.log_ACTIVITY_HI_Hello(greeting);
        ctx.tlmWrite_HelloCount(self.hello_count);
        CmdResponse::Ok
    }
}
