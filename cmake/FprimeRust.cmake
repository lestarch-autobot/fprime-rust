####
# FprimeRust.cmake:
#
# `include(FprimeRust)` from a deployment's CMakeLists.txt (after FPrime.cmake, before
# fprime_setup_included_code) registers the fprime_rust autocoder/target for normal and unit-test builds and
# locates cargo. Constants: FPRIME_RUST_CARGO (configure fails naming it when absent, REQ-FprimeRust-035),
# FPRIME_RUST_PROFILE (default release), FPRIME_RUST_TARGET (default host triple).
####
include_guard()
if (DEFINED FPRIME_SUB_BUILD_TARGETS)
    return()
endif()
set(FPRIME_RUST_RUNTIME_DIR "${CMAKE_CURRENT_LIST_DIR}/../runtime" CACHE PATH "fprime-rust runtime crate")
get_filename_component(FPRIME_RUST_RUNTIME_DIR "${FPRIME_RUST_RUNTIME_DIR}" ABSOLUTE)
set(FPRIME_RUST_PROFILE "release" CACHE STRING "Cargo profile used for Rust components")
if (NOT DEFINED FPRIME_RUST_CARGO OR "${FPRIME_RUST_CARGO}" STREQUAL "")
    find_program(FPRIME_RUST_CARGO NAMES cargo PATHS "$ENV{HOME}/.cargo/bin" "$ENV{CARGO_HOME}/bin")
endif()
if (NOT FPRIME_RUST_CARGO OR NOT EXISTS "${FPRIME_RUST_CARGO}")
    message(FATAL_ERROR "[fprime_rust] cargo not found: set FPRIME_RUST_CARGO to the cargo executable (got '${FPRIME_RUST_CARGO}')")
endif()
if (NOT DEFINED FPRIME_RUST_TARGET OR "${FPRIME_RUST_TARGET}" STREQUAL "")
    execute_process(COMMAND "${FPRIME_RUST_CARGO}" -vV OUTPUT_VARIABLE CARGO_VERSION_OUTPUT COMMAND_ERROR_IS_FATAL ANY)
    string(REGEX MATCH "host: ([^\n]+)" _HOST_MATCH "${CARGO_VERSION_OUTPUT}")
    set(FPRIME_RUST_TARGET "${CMAKE_MATCH_1}" CACHE STRING "Rust target triple for Rust components")
endif()
# System libraries the Rust std needs (cargo's `native-static-libs` is only known at build time, so the list is fixed
# per platform; other platforms override it through the cache variable)
if (CMAKE_SYSTEM_NAME STREQUAL "Linux")
    set(_FPRIME_RUST_NATIVE_LIBS_DEFAULT pthread dl m rt util gcc_s c)  # rustc --print native-static-libs on glibc
else()
    set(_FPRIME_RUST_NATIVE_LIBS_DEFAULT pthread dl m)
endif()
set(FPRIME_RUST_NATIVE_LIBS "${_FPRIME_RUST_NATIVE_LIBS_DEFAULT}" CACHE STRING
    "System libraries linked after the Rust archive (cargo native-static-libs equivalent)")
set(FPRIME_RUST_SYSTEM_LIBRARIES ${FPRIME_RUST_NATIVE_LIBS})
message(STATUS "[fprime_rust] cargo: ${FPRIME_RUST_CARGO}; target: ${FPRIME_RUST_TARGET}; profile: ${FPRIME_RUST_PROFILE}")
register_fprime_target(target/fprime_rust)
register_fprime_ut_target(target/fprime_rust)
