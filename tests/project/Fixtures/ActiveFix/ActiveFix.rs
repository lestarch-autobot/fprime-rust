//! `Fix.ActiveFix`: active shim fixture (see ActiveFix.fpp)
use crate::activefix_base::*;

pub struct ActiveFix;

impl Component for ActiveFix {
    fn new() -> Self {
        ActiveFix
    }

    fn aIn_handler(&mut self, ctx: &mut Context<'_>, _port_num: FwIndexType, x: u32) {
        ctx.tlmWrite_T_X(x);
    }

    fn AC_cmd_handler(&mut self, ctx: &mut Context<'_>, x: u32) -> CmdResponse {
        ctx.log_ACTIVITY_LO_E_X(x);
        CmdResponse::Ok
    }
}
