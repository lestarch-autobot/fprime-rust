//! `Fix.ActiveFix`: active shim fixture (see ActiveFix.fpp)
use crate::activefix_base::*;

pub struct ActiveFix;

impl Component for ActiveFix {
    fn new() -> Self {
        ActiveFix
    }

    fn aIn_handler(&mut self, ctx: &mut Context<'_>, _port_num: FwIndexType, x: u32) {
        if x == 777 {
            std::thread::sleep(std::time::Duration::from_millis(200));
        }
        ctx.tlmWrite_T_X(x);
    }

    fn gIn_handler(&mut self, ctx: &mut Context<'_>, _port_num: FwIndexType, x: u32) {
        ctx.tlmWrite_T_X(x);
        ctx.tlmWrite_T_DROPPED(ctx.num_msgs_dropped() as u32);
        ctx.tlmWrite_T_RESP(CmdResponse::Ok);
    }

    fn AC_cmd_handler(&mut self, ctx: &mut Context<'_>, x: u32) -> CmdResponse {
        ctx.log_ACTIVITY_LO_E_X(x);
        CmdResponse::Ok
    }
}
