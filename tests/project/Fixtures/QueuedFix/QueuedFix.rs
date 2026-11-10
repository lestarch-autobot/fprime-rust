//! `Fix.QueuedFix`: queued shim fixture (see QueuedFix.fpp)
use crate::queuedfix_base::*;
use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};
use std::sync::Mutex;
use std::time::Duration;

/// (mark, hash of the thread that recorded it)
static TRACE: Mutex<Vec<(u32, u64)>> = Mutex::new(Vec::new());

fn thread_hash() -> u64 {
    let mut hasher = DefaultHasher::new();
    std::thread::current().id().hash(&mut hasher);
    hasher.finish()
}

fn trace(mark: u32) {
    TRACE.lock().unwrap().push((mark, thread_hash()));
}

#[no_mangle]
pub extern "C" fn fix_queued_current_thread() -> u64 {
    thread_hash()
}

#[no_mangle]
pub extern "C" fn fix_queued_reset() {
    TRACE.lock().unwrap().clear();
}

/// Copies marks and thread hashes into `marks`/`threads` (at most `capacity`) and returns the trace length
#[no_mangle]
pub unsafe extern "C" fn fix_queued_trace(marks: *mut u32, threads: *mut u64, capacity: usize) -> usize {
    let trace = TRACE.lock().unwrap();
    for (index, (mark, thread)) in trace.iter().take(capacity).enumerate() {
        // SAFETY: the tester passes arrays of `capacity` entries
        unsafe {
            *marks.add(index) = *mark;
            *threads.add(index) = *thread;
        }
    }
    trace.len()
}

pub struct QueuedFix;

impl Component for QueuedFix {
    fn new() -> Self {
        QueuedFix
    }

    fn aIn_handler(&mut self, ctx: &mut Context<'_>, _port_num: FwIndexType, x: u32) {
        trace(100 + x);
        let invocations = if x >= 70 { 3 } else { u32::from(x >= 50) };
        for _ in 0..invocations {
            ctx.ip_internal_invoke(x);
        }
    }

    fn aIn_overflow_hook(&mut self, _ctx: &mut Context<'_>, _port_num: FwIndexType, x: u32) {
        trace(900 + x);
    }

    fn sIn_handler(&mut self, _ctx: &mut Context<'_>, _port_num: FwIndexType, x: u32) {
        trace(500 + x);
        std::thread::sleep(Duration::from_millis(50));
        trace(600 + x);
    }

    fn run_handler(&mut self, ctx: &mut Context<'_>, _port_num: FwIndexType, _context: u32) {
        trace(1000 + ctx.last_dispatch() as u32);
        ctx.tlmWrite_T_DROPPED(ctx.num_msgs_dropped() as u32);
    }

    fn ip_internal_handler(&mut self, _ctx: &mut Context<'_>, x: u32) {
        trace(300 + x);
    }

    fn ip_overflow_hook(&mut self, _ctx: &mut Context<'_>, x: u32) {
        trace(700 + x);
    }

    fn AC_cmd_handler(&mut self, _ctx: &mut Context<'_>, x: u32) -> CmdResponse {
        trace(200 + x);
        CmdResponse::Ok
    }

    fn AC_overflow_hook(&mut self, _ctx: &mut Context<'_>, _opcode: FwOpcodeType, _cmd_seq: u32) -> CmdResponse {
        CmdResponse::Busy
    }
}
