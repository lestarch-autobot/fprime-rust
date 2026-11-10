//! UT-RT-3 (REQ-FprimeRust-024): a panic reaches `fprime_rust_assert` with the Rust `file:line`, then aborts.
//!
//! The C++ runtime is not linked into cargo tests, so this test provides `fprime_rust_assert` itself, as the
//! F Prime assertion hook would observe it, then aborts the child process like the real one (death test).
#![allow(missing_docs)]
use std::process::Command;

#[no_mangle]
pub extern "C" fn fprime_rust_assert(file: *const u8, file_len: u64, line: u32, msg: *const u8, msg_len: u64) -> ! {
    let file = unsafe { std::str::from_utf8_unchecked(std::slice::from_raw_parts(file, file_len as usize)) };
    let msg = unsafe { std::str::from_utf8_unchecked(std::slice::from_raw_parts(msg, msg_len as usize)) };
    eprintln!("ASSERT_HOOK {}:{} {}", file, line, msg);
    std::process::abort()
}

#[no_mangle]
pub extern "C" fn fprime_rust_string_assign(_carrier: *mut std::ffi::c_void, _bytes: *const u8, _len: usize) {}

fn handler_that_panics() {
    panic!("handler failure");
}

#[test]
fn panic_reaches_assert_hook_with_file_and_line_then_aborts() {
    if std::env::var("FPRIME_RUST_DEATH_CHILD").is_ok() {
        fprime_rust::install_panic_hook();
        fprime_rust::install_panic_hook(); // idempotent
        handler_that_panics();
        unreachable!();
    }
    let output = Command::new(std::env::current_exe().unwrap())
        .arg("panic_reaches_assert_hook_with_file_and_line_then_aborts")
        .arg("--exact")
        .arg("--nocapture")
        .env("FPRIME_RUST_DEATH_CHILD", "1")
        .output()
        .unwrap();
    let stderr = String::from_utf8_lossy(&output.stderr);
    assert!(!output.status.success(), "child must abort: {stderr}");
    #[cfg(unix)]
    {
        use std::os::unix::process::ExitStatusExt;
        assert_eq!(output.status.signal(), Some(libc_sigabrt()), "child must die of SIGABRT: {stderr}");
    }
    let line_of_panic = stderr
        .lines()
        .find(|l| l.starts_with("ASSERT_HOOK "))
        .unwrap_or_else(|| panic!("no hook line in {stderr}"));
    assert!(line_of_panic.starts_with(&format!("ASSERT_HOOK {}:", file!())), "{line_of_panic}");
    assert!(line_of_panic.ends_with("handler failure"), "{line_of_panic}");
}

#[cfg(unix)]
fn libc_sigabrt() -> i32 {
    6
}
