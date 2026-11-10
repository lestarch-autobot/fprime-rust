####
# target/fprime_rust.cmake:
#
# Runs the fprime_rust autocoder on every module, strips `.rs` files from the compiled sources and records them
# (`FPRIME_RUST_SOURCES`). For each executable (deployment or unit test) it collects the Rust components of the
# full dependency list, emits ONE Cargo workspace (`fprime-rust-ac crate`), builds it with cargo and links the
# single resulting static archive `libfprime_rust_<Executable>.a` (REQ-FprimeRust-018/-019/-020/-039).
####
include_guard()
include(autocoder/autocoder)
include(utilities)

function(fprime_rust_add_global_target TARGET)
endfunction(fprime_rust_add_global_target)

function(fprime_rust_add_module_target MODULE TARGET SOURCE_FILES DEPENDENCIES)
    run_ac_set("${MODULE}" "autocoder/fprime_rust")
    # `.rs` files are inputs to cargo, never to the C++ compiler
    get_target_property(MODULE_SOURCES "${MODULE}" SOURCES)
    if (MODULE_SOURCES)
        set(RUST_SOURCES "${MODULE_SOURCES}")
        list(FILTER RUST_SOURCES INCLUDE REGEX "^.*\\.rs$")
        list(FILTER MODULE_SOURCES EXCLUDE REGEX "^.*\\.rs$")
        set_target_properties("${MODULE}" PROPERTIES SOURCES "${MODULE_SOURCES}")
        if (RUST_SOURCES)
            append_list_property("${RUST_SOURCES}" TARGET "${MODULE}" PROPERTY FPRIME_RUST_SOURCES)
        endif()
    endif()
    # A unit-test executable links its own archive, built from its full dependency list (REQ-FprimeRust-019)
    get_target_property(MODULE_TYPE "${MODULE}" FPRIME_TYPE)
    if (MODULE_TYPE STREQUAL "Unit Test")
        recurse_target_properties("${MODULE}" "FPRIME_DEPENDENCIES" FULL_DEPENDENCIES EXTERNAL_DEPENDENCIES UNKNOWN)
        fprime_rust_link_archive("${MODULE}" "${FULL_DEPENDENCIES}")
    endif()
endfunction(fprime_rust_add_module_target)

function(fprime_rust_add_deployment_target MODULE TARGET SOURCES DEPENDENCIES FULL_DEPENDENCIES)
    fprime_rust_add_module_target("${MODULE}" "${TARGET}" "${SOURCES}" "${DEPENDENCIES}")
    fprime_rust_link_archive("${MODULE}" "${FULL_DEPENDENCIES}")
endfunction(fprime_rust_add_deployment_target)

####
# fprime_rust_link_archive: build and link the one Rust archive of executable EXECUTABLE
####
function(fprime_rust_link_archive EXECUTABLE FULL_DEPENDENCIES)
    if (TARGET "${EXECUTABLE}_fprime_rust")
        return()  # deployments see both the normal and the unit-test target list
    endif()
    set(COMPONENT_SPECS)
    set(COMPONENT_MODULES)
    foreach(DEPENDENCY IN LISTS FULL_DEPENDENCIES EXECUTABLE)
        if (NOT TARGET "${DEPENDENCY}")
            continue()
        endif()
        get_target_property(SPECS "${DEPENDENCY}" FPRIME_RUST_COMPONENTS)
        if (SPECS)
            list(APPEND COMPONENT_SPECS ${SPECS})
            list(APPEND COMPONENT_MODULES "${DEPENDENCY}")
        endif()
    endforeach()
    if (NOT COMPONENT_SPECS)
        return()  # no Rust component: no workspace, no cargo, no archive (REQ-FprimeRust-039)
    endif()
    list(REMOVE_DUPLICATES COMPONENT_SPECS)
    list(SORT COMPONENT_SPECS)
    find_program(FPRIME_RUST_AC NAMES fprime-rust-ac REQUIRED)
    set(WORKSPACE_DIR "${CMAKE_CURRENT_BINARY_DIR}/fprime_rust/${EXECUTABLE}")
    set(COMPONENT_ARGUMENTS)
    set(RUST_INPUTS)
    foreach(SPEC IN LISTS COMPONENT_SPECS)
        list(APPEND COMPONENT_ARGUMENTS "--component" "${SPEC}")
        string(REPLACE "=" ";" SPEC_PARTS "${SPEC}")
        list(GET SPEC_PARTS 1 BASE_FILE)
        list(GET SPEC_PARTS 2 USER_FILE)
        list(APPEND RUST_INPUTS "${BASE_FILE}" "${USER_FILE}")
    endforeach()
    execute_process(
        COMMAND "${FPRIME_RUST_AC}" "crate" "--output-directory" "${WORKSPACE_DIR}" "--target" "${EXECUTABLE}"
            "--runtime" "${FPRIME_RUST_RUNTIME_DIR}" ${COMPONENT_ARGUMENTS}
        COMMAND_ERROR_IS_FATAL ANY
    )
    if (FPRIME_RUST_PROFILE STREQUAL "dev")
        set(PROFILE_DIR "debug")
    else()
        set(PROFILE_DIR "${FPRIME_RUST_PROFILE}")
    endif()
    set(ARCHIVE "${WORKSPACE_DIR}/target/${FPRIME_RUST_TARGET}/${PROFILE_DIR}/${CMAKE_STATIC_LIBRARY_PREFIX}fprime_rust_${EXECUTABLE}${CMAKE_STATIC_LIBRARY_SUFFIX}")
    file(GLOB_RECURSE RUNTIME_SOURCES "${FPRIME_RUST_RUNTIME_DIR}/src/*.rs")
    add_custom_command(
        OUTPUT "${ARCHIVE}"
        COMMAND "${CMAKE_COMMAND}" -E env CARGO_TERM_COLOR=never "${FPRIME_RUST_CARGO}" build
            --profile "${FPRIME_RUST_PROFILE}" --target "${FPRIME_RUST_TARGET}"
            --target-dir "${WORKSPACE_DIR}/target" --manifest-path "${WORKSPACE_DIR}/Cargo.toml"
        DEPENDS ${RUST_INPUTS} ${RUNTIME_SOURCES} "${FPRIME_RUST_RUNTIME_DIR}/Cargo.toml" "${WORKSPACE_DIR}/Cargo.toml"
        WORKING_DIRECTORY "${WORKSPACE_DIR}"
        COMMENT "[fprime_rust] cargo build of ${EXECUTABLE} Rust components"
        VERBATIM
    )
    add_custom_target("${EXECUTABLE}_fprime_rust" DEPENDS "${ARCHIVE}")
    add_dependencies("${EXECUTABLE}_fprime_rust" ${COMPONENT_MODULES})
    add_dependencies("${EXECUTABLE}" "${EXECUTABLE}_fprime_rust")
    # The archive is linked through each Rust module's INTERFACE link (autocoder/fprime_rust) so it follows the
    # shim objects defining the helpers it references; the runtime and Rust std's system libraries follow
    set_property(TARGET "${EXECUTABLE}" PROPERTY FPRIME_RUST_ARCHIVE "${ARCHIVE}")
    target_link_libraries("${EXECUTABLE}" PRIVATE FprimeRust ${FPRIME_RUST_SYSTEM_LIBRARIES})
    message(STATUS "[fprime_rust] ${EXECUTABLE} links ${ARCHIVE}")
endfunction(fprime_rust_link_archive)
