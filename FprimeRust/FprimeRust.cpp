// fprime-rust support library translation unit.
//
// Intentionally empty: the runtime is owned by the ``fprime-rust``
// Cargo crate, and the per-component shims include only ``<Component>.hpp``.
// This source file exists to satisfy CMake's ``add_library`` requirement
// for at least one source per static library target; future versions
// may expose shared C++ utilities here.
#include <FprimeRust/FprimeRust.hpp>
