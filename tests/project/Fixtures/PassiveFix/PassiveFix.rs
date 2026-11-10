//! `Fix.PassiveFix`: shim fixture (see PassiveFix.fpp); counters and the trace are exported to the GTest tester
use crate::passivefix_base::*;
use std::sync::atomic::{AtomicU32, Ordering};
use std::sync::Mutex;
use std::time::Duration;

static TRACE: Mutex<Vec<u32>> = Mutex::new(Vec::new());
/// new, init, drop, parameter_updated
static COUNTS: [AtomicU32; 4] = [AtomicU32::new(0), AtomicU32::new(0), AtomicU32::new(0), AtomicU32::new(0)];

fn bump(index: usize) {
    COUNTS[index].fetch_add(1, Ordering::SeqCst);
}

fn trace(mark: u32) {
    TRACE.lock().unwrap().push(mark);
}

#[no_mangle]
pub extern "C" fn fix_passive_count(index: u32) -> u32 {
    COUNTS[index as usize].load(Ordering::SeqCst)
}

#[no_mangle]
pub extern "C" fn fix_passive_reset() {
    COUNTS.iter().for_each(|count| count.store(0, Ordering::SeqCst));
    TRACE.lock().unwrap().clear();
}

/// Copies the trace into `out` (at most `capacity` entries) and returns the trace length
#[no_mangle]
pub unsafe extern "C" fn fix_passive_trace(out: *mut u32, capacity: usize) -> usize {
    let trace = TRACE.lock().unwrap();
    for (index, mark) in trace.iter().take(capacity).enumerate() {
        // SAFETY: the tester passes an array of `capacity` u32
        unsafe { *out.add(index) = *mark };
    }
    trace.len()
}

pub struct PassiveFix;

impl Drop for PassiveFix {
    fn drop(&mut self) {
        bump(2);
    }
}

impl Component for PassiveFix {
    fn new() -> Self {
        bump(0);
        PassiveFix
    }

    fn init(&mut self, _ctx: &InitContext<'_>) {
        bump(1);
    }

    fn parameter_updated(&mut self, _ctx: &mut Context<'_>, _id: FwPrmIdType) {
        bump(3);
    }

    fn sIn_handler(&mut self, ctx: &mut Context<'_>, port_num: FwIndexType, a: u32, s: &str, m: Mode) -> u32 {
        ctx.tlmWrite_T_STR(s);
        ctx.vOut_out(port_num, a, s, m).wrapping_add(1)
    }

    fn gIn_handler(&mut self, _ctx: &mut Context<'_>, _port_num: FwIndexType, a: u32, s: &str, m: Mode) -> u32 {
        a.wrapping_mul(2) + u32::from(m.repr()) + s.len() as u32
    }

    fn strIn_handler(&mut self, ctx: &mut Context<'_>, _port_num: FwIndexType, s: &str) {
        ctx.tlmWrite_T_STR(s);
        ctx.sOut_out(0, s);
    }

    fn slowIn_handler(&mut self, _ctx: &mut Context<'_>, _port_num: FwIndexType, x: u32) {
        trace(x * 10);
        std::thread::sleep(Duration::from_millis(50));
        trace(x * 10 + 1);
    }

    fn SC_cmd_handler(&mut self, _ctx: &mut Context<'_>, m: Mode) -> CmdResponse {
        match m {
            Mode::ON => CmdResponse::Ok,
            Mode::OFF => CmdResponse::ValidationError,
        }
    }

    fn GC_cmd_handler(&mut self, ctx: &mut Context<'_>, s: &str) -> CmdResponse {
        ctx.log_ACTIVITY_LO_E_S200(s);
        CmdResponse::Ok
    }

    fn EMIT_cmd_handler(&mut self, ctx: &mut Context<'_>, kind: u32) -> CmdResponse {
        match kind {
            1 => {
                let long = "x".repeat(48);
                ctx.log_ACTIVITY_LO_E_S40(&long);
                ctx.tlmWrite_T_STR(&long);
            }
            2 => ctx.log_ACTIVITY_LO_E_S40("ab\0cd"),
            _ => return CmdResponse::ValidationError,
        }
        CmdResponse::Ok
    }

    fn LOG_ALL_cmd_handler(&mut self, ctx: &mut Context<'_>, x: u32) -> CmdResponse {
        ctx.log_ACTIVITY_LO_E_ALO(x);
        ctx.log_ACTIVITY_HI_E_AHI(x);
        ctx.log_WARNING_LO_E_WLO(x);
        ctx.log_WARNING_HI_E_WHI(x);
        ctx.log_COMMAND_E_CMD(x);
        ctx.log_DIAGNOSTIC_E_DIAG(x);
        CmdResponse::Ok
    }

    fn FATAL_NOW_cmd_handler(&mut self, ctx: &mut Context<'_>, x: u32) -> CmdResponse {
        ctx.log_FATAL_E_FATAL(x);
        CmdResponse::Ok
    }

    fn TLM_ALL_cmd_handler(&mut self, ctx: &mut Context<'_>, x: u32) -> CmdResponse {
        ctx.tlmWrite_T_U32(x);
        ctx.tlmWrite_T_I8(-(x as i8));
        ctx.tlmWrite_T_F64(f64::from(x) / 2.0);
        ctx.tlmWrite_T_BOOL(x != 0);
        ctx.tlmWrite_T_MODE(if x != 0 { Mode::ON } else { Mode::OFF });
        CmdResponse::Ok
    }

    fn PRM_cmd_handler(&mut self, ctx: &mut Context<'_>) -> CmdResponse {
        let (value, valid) = ctx.paramGet_P_U32();
        ctx.tlmWrite_T_PRM(value);
        ctx.tlmWrite_T_VALID(u32::from(valid.code()));
        let (value, valid) = ctx.paramGet_P_NODEF();
        ctx.tlmWrite_T_PRM2(value);
        ctx.tlmWrite_T_VALID2(u32::from(valid.code()));
        CmdResponse::Ok
    }

    fn PANIC_cmd_handler(&mut self, _ctx: &mut Context<'_>, really: bool) -> CmdResponse {
        if really {
            panic!("fixture panic")
        }
        CmdResponse::Ok
    }
}
