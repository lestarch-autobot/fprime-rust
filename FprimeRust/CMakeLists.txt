####
# FprimeRust: C++ side of the fprime-rust runtime (context, lock, string copying, panic bridge).
# Every Rust shim links this module; the Rust runtime crate's extern "C" references resolve here.
####
register_fprime_library(
        FprimeRust
    SOURCES
        "${CMAKE_CURRENT_LIST_DIR}/FprimeRust.cpp"
    HEADERS
        "${CMAKE_CURRENT_LIST_DIR}/FprimeRust.hpp"
    DEPENDS
        Fw_Types
        Fw_Logger
        Os
)
