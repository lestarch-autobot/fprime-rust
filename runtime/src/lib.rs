//! fprime-rust runtime: the pieces shared by every generated Rust component base module.
//!
//! * [`RawContext`] mirrors the C++ `FprimeRustContext` handed to each FFI entry.
//! * [`CmdResponse`], [`ParamValid`] and [`MsgDispatchStatus`] mirror their F Prime enumerations.
//! * [`str_arg`] and [`StrOut`] carry strings over the FFI as borrowed `(ptr, len)` pairs.
//! * [`install_panic_hook`] forwards every panic to the F Prime assertion hook, then aborts (REQ-FprimeRust-024).

use std::borrow::Cow;
use std::ffi::c_void;
use std::marker::PhantomData;
use std::sync::Once;

/// Call context shared with C++. Layout is `FprimeRustContext` in `FprimeRust/FprimeRust.hpp`.
#[repr(C)]
#[derive(Debug)]
pub struct RawContext {
    /// The C++ shim instance that owns the call
    pub component: *mut c_void,
    /// `Fw::QueuedComponentBase::MsgDispatchStatus` of the queue drain that preceded this call (queued kind)
    pub last_dispatch: u32,
}

/// Marker type making any holder neither `Send` nor `Sync`: a context borrows one shim stack frame on one
/// thread for one call (REQ-FprimeRust-023).
#[derive(Debug, Default)]
pub struct NotThreadSafe(PhantomData<*mut ()>);

impl NotThreadSafe {
    /// Create the marker
    pub const fn new() -> Self {
        NotThreadSafe(PhantomData)
    }
}

/// `Fw::CmdResponse`: the completion status a command handler returns (REQ-FprimeRust-012)
#[repr(u32)]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CmdResponse {
    /// Command successfully executed
    Ok = 0,
    /// Invalid opcode dispatched
    InvalidOpcode = 1,
    /// Command failed validation
    ValidationError = 2,
    /// Command failed to deserialize
    FormatError = 3,
    /// Command had execution error
    ExecutionError = 4,
    /// Component busy
    Busy = 5,
}

impl CmdResponse {
    /// The F Prime integer code
    pub const fn code(self) -> u32 {
        self as u32
    }

    /// Decode an F Prime integer code
    pub const fn from_code(code: u32) -> Option<Self> {
        match code {
            0 => Some(CmdResponse::Ok),
            1 => Some(CmdResponse::InvalidOpcode),
            2 => Some(CmdResponse::ValidationError),
            3 => Some(CmdResponse::FormatError),
            4 => Some(CmdResponse::ExecutionError),
            5 => Some(CmdResponse::Busy),
            _ => None,
        }
    }
}

/// `Fw::ParamValid`: the validity of a parameter value (REQ-FprimeRust-015)
#[repr(u8)]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ParamValid {
    /// Parameter storage not yet initialized
    Uninit = 0,
    /// The stored value
    Valid = 1,
    /// The stored value could not be deserialized
    Invalid = 2,
    /// The FPP default value
    Default = 3,
}

impl ParamValid {
    /// The F Prime integer code
    pub const fn code(self) -> u8 {
        self as u8
    }

    /// Decode an F Prime integer code; unknown codes decode as `Invalid`
    pub const fn from_code(code: u8) -> Self {
        match code {
            0 => ParamValid::Uninit,
            1 => ParamValid::Valid,
            3 => ParamValid::Default,
            _ => ParamValid::Invalid,
        }
    }
}

/// `Fw::QueuedComponentBase::MsgDispatchStatus`: result of the queue drain preceding a sync/guarded entry
#[repr(u32)]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum MsgDispatchStatus {
    /// Dispatch was normal
    Ok = 0,
    /// No more messages in the queue
    Empty = 1,
    /// Errors dispatching messages
    Error = 2,
    /// A message was sent requesting an exit of the loop
    Exit = 3,
}

impl MsgDispatchStatus {
    /// The F Prime integer code
    pub const fn code(self) -> u32 {
        self as u32
    }

    /// Decode an F Prime integer code; unknown codes decode as `Error`
    pub const fn from_code(code: u32) -> Self {
        match code {
            0 => MsgDispatchStatus::Ok,
            1 => MsgDispatchStatus::Empty,
            3 => MsgDispatchStatus::Exit,
            _ => MsgDispatchStatus::Error,
        }
    }
}

/// View a borrowed C++ string argument as `&str`; invalid UTF-8 becomes U+FFFD (REQ-FprimeRust-038).
///
/// # Safety
/// `ptr` must point to `len` readable bytes that stay valid and unmodified for the returned lifetime.
pub unsafe fn str_arg<'a>(ptr: *const u8, len: usize) -> Cow<'a, str> {
    if ptr.is_null() || len == 0 {
        return Cow::Borrowed("");
    }
    // SAFETY: the caller guarantees `len` readable bytes at `ptr` for `'a`
    String::from_utf8_lossy(unsafe { std::slice::from_raw_parts(ptr, len) })
}

/// A Rust string passed to C++ as a borrowed `(ptr, len)` pair
pub trait StrOut {
    /// Pointer to the first byte (never null, for empty strings a dangling non-null pointer)
    fn out_ptr(&self) -> *const u8;
    /// Byte length
    fn out_len(&self) -> usize;
}

impl StrOut for str {
    fn out_ptr(&self) -> *const u8 {
        self.as_ptr()
    }
    fn out_len(&self) -> usize {
        self.len()
    }
}

impl StrOut for String {
    fn out_ptr(&self) -> *const u8 {
        self.as_ptr()
    }
    fn out_len(&self) -> usize {
        self.len()
    }
}

extern "C" {
    /// C++ runtime (FprimeRust/FprimeRust.cpp): report a panic to the F Prime assertion hook and abort
    pub fn fprime_rust_assert(file: *const u8, file_len: u64, line: u32, msg: *const u8, msg_len: u64) -> !;
    /// C++ runtime: assign bytes into a `Fw::StringBase` carrier (truncating to capacity and interior NUL)
    pub fn fprime_rust_string_assign(carrier: *mut c_void, bytes: *const u8, len: u64);
    /// C++ runtime marker: one definition per executable (REQ-FprimeRust-020)
    pub fn fprime_rust_runtime_marker() -> u32;
}

/// Assign a Rust string into a `Fw::StringBase` carrier owned by C++ (port string return values).
///
/// # Safety
/// `carrier` must be a valid `Fw::StringBase*` for the duration of the call.
pub unsafe fn assign_string(carrier: *mut c_void, value: &str) {
    // SAFETY: the caller guarantees a valid carrier; `value` is borrowed for the call
    unsafe { fprime_rust_string_assign(carrier, value.as_ptr(), value.len() as u64) }
}

static PANIC_HOOK: Once = Once::new();

/// Install the process-wide panic hook once: message and `file:line` go to `fprime_rust_assert`, which
/// reaches the F Prime assertion hook and aborts (REQ-FprimeRust-024). Idempotent.
pub fn install_panic_hook() {
    PANIC_HOOK.call_once(|| {
        std::panic::set_hook(Box::new(|info| {
            let message: Cow<str> = if let Some(s) = info.payload().downcast_ref::<&str>() {
                Cow::Borrowed(s)
            } else if let Some(s) = info.payload().downcast_ref::<String>() {
                Cow::Borrowed(s.as_str())
            } else {
                Cow::Borrowed("panic")
            };
            let (file, line) = match info.location() {
                Some(location) => (location.file(), location.line()),
                None => ("<unknown>", 0),
            };
            // SAFETY: both strings are borrowed for the call; the callee never returns
            unsafe {
                fprime_rust_assert(
                    file.as_ptr(),
                    file.len() as u64,
                    line,
                    message.as_ptr(),
                    message.len() as u64,
                )
            }
        }));
    });
}

/// Decode an FFI enum carrier or panic (which reaches the assertion hook): the C++ side only ever
/// produces values of the FPP enumeration.
pub fn enum_from_repr<T, R: std::fmt::Debug + Copy>(value: R, decode: fn(R) -> Option<T>, name: &str) -> T {
    match decode(value) {
        Some(decoded) => decoded,
        None => panic!("invalid {} enumeration value {:?} received over the FFI", name, value),
    }
}
