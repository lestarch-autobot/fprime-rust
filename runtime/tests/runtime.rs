//! UT-RT-1 and UT-RT-2 (REQ-FprimeRust-012, -015, -023)
use fprime_rust::{CmdResponse, MsgDispatchStatus, NotThreadSafe, ParamValid, RawContext};
use static_assertions::assert_not_impl_any;

/// The shape every generated `Context<'call>` has: a borrowed raw context plus the marker
struct Context<'call> {
    _raw: &'call mut RawContext,
    _marker: NotThreadSafe,
}

assert_not_impl_any!(Context<'static>: Send, Sync);
assert_not_impl_any!(RawContext: Send, Sync);

#[test]
fn cmd_response_round_trips_fprime_codes() {
    let table = [
        (CmdResponse::Ok, 0),
        (CmdResponse::InvalidOpcode, 1),
        (CmdResponse::ValidationError, 2),
        (CmdResponse::FormatError, 3),
        (CmdResponse::ExecutionError, 4),
        (CmdResponse::Busy, 5),
    ];
    for (value, code) in table {
        assert_eq!(value.code(), code);
        assert_eq!(CmdResponse::from_code(code), Some(value));
    }
    assert_eq!(CmdResponse::from_code(6), None);
}

#[test]
fn param_valid_round_trips_fprime_codes() {
    for (value, code) in [
        (ParamValid::Uninit, 0),
        (ParamValid::Valid, 1),
        (ParamValid::Invalid, 2),
        (ParamValid::Default, 3),
    ] {
        assert_eq!(value.code(), code);
        assert_eq!(ParamValid::from_code(code), value);
    }
    assert_eq!(ParamValid::from_code(200), ParamValid::Invalid);
}

#[test]
fn msg_dispatch_status_round_trips_fprime_codes() {
    for (value, code) in [
        (MsgDispatchStatus::Ok, 0),
        (MsgDispatchStatus::Empty, 1),
        (MsgDispatchStatus::Error, 2),
        (MsgDispatchStatus::Exit, 3),
    ] {
        assert_eq!(value.code(), code);
        assert_eq!(MsgDispatchStatus::from_code(code), value);
    }
    assert_eq!(MsgDispatchStatus::from_code(99), MsgDispatchStatus::Error);
}

#[test]
fn str_arg_replaces_invalid_utf8_and_handles_null() {
    let bytes = [0xFFu8, 0x41];
    let text = unsafe { fprime_rust::str_arg(bytes.as_ptr(), bytes.len()) };
    assert_eq!(&*text, "\u{FFFD}A");
    assert_eq!(&*unsafe { fprime_rust::str_arg(std::ptr::null(), 5) }, "");
    let ok = b"ok";
    assert_eq!(&*unsafe { fprime_rust::str_arg(ok.as_ptr(), ok.len()) }, "ok");
}
