// ======================================================================
// \title  FprimeRust.hpp
// \brief  C++ side of the fprime-rust runtime: the call context handed to Rust, the instance lock, string
//         carrier copying (REQ-FprimeRust-037) and the panic-to-assert bridge (REQ-FprimeRust-024)
// ======================================================================
#ifndef FPRIME_RUST_FPRIME_RUST_HPP
#define FPRIME_RUST_FPRIME_RUST_HPP

#include <Fw/Types/BasicTypes.hpp>
#include <Fw/Types/StringBase.hpp>
#include <Os/Mutex.hpp>

//! Context handed over the FFI for one call. Mirrors `fprime_rust::RawContext` (#[repr(C)]) exactly.
struct FprimeRustContext {
    void* component;   //!< The shim instance the Rust helpers call back into
    U32 last_dispatch; //!< Fw::QueuedComponentBase::MsgDispatchStatus of the queue drain preceding the call
};

extern "C" {
//! Exported runtime marker; exactly one definition per executable (REQ-FprimeRust-020)
U32 fprime_rust_runtime_marker();

//! Rust panic bridge: log `msg`, report `file:line` to the F Prime assertion hook, then abort
void fprime_rust_assert(const CHAR* file, FwSizeType fileLength, U32 line, const CHAR* msg, FwSizeType msgLength);

//! Assign `length` bytes of `bytes` into the Fw::StringBase at `carrier`, truncating to capacity and interior NUL
void fprime_rust_string_assign(void* carrier, const CHAR* bytes, FwSizeType length);
}

namespace FprimeRust {

//! Copy `length` bytes of a borrowed Rust string into `destination[destinationSize]` as a NUL-terminated C
//! string: truncated to `destinationSize - 1` bytes and at the first interior NUL (REQ-FprimeRust-037).
//! Returns the number of bytes stored.
FwSizeType copyBytes(CHAR* destination, FwSizeType destinationSize, const CHAR* bytes, FwSizeType length);

//! Copy a borrowed Rust string into an F Prime string carrier: truncated to the carrier's capacity and at the
//! first interior NUL (REQ-FprimeRust-037)
void assignString(Fw::StringBase& destination, const CHAR* bytes, FwSizeType length);

//! RAII guard over the shim's non-recursive instance mutex (mutex rule, REQ-FprimeRust-023)
class Lock {
  public:
    explicit Lock(Os::Mutex& mutex) : m_mutex(mutex) { this->m_mutex.lock(); }
    ~Lock() { this->m_mutex.unLock(); }
    Lock(const Lock&) = delete;
    Lock& operator=(const Lock&) = delete;

  private:
    Os::Mutex& m_mutex;
};

}  // namespace FprimeRust

#endif  // FPRIME_RUST_FPRIME_RUST_HPP
