####
# F Prime CMakeLists.txt:
#
# SOURCES: list of source files; the `.rs` is the Rust implementation picked up by the fprime-rust autocoder
# AUTOCODER_INPUTS: list of files to be passed to the autocoders
# DEPENDS: list of libraries that this module depends on
####
register_fprime_module(
    AUTOCODER_INPUTS
        "${CMAKE_CURRENT_LIST_DIR}/{{cookiecutter.component_name}}.fpp"
    SOURCES
        "${CMAKE_CURRENT_LIST_DIR}/{{cookiecutter.component_name}}.rs"
)
