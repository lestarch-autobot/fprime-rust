####
# autocoder/fprime_rust.cmake:
#
# Per-module autocoder: runs `fprime-rust-ac bindings` on the module's `.fpp` translation units. The model is
# analyzed in-process from the module's `fpp-cache/stdout.txt` closure; no JSON model is involved. Returns the
# C++ shim as a build source and the `.hpp`/`.rs` outputs as other generated files, and records the module's Rust
# components (`FPRIME_RUST_COMPONENTS`, as `Ns.Comp=<base.rs>=<Comp.rs>`) for `target/fprime_rust`.
####
include_guard()
include(utilities)
include(autocoder/helpers)

autocoder_setup_for_multiple_sources()

function(fprime_rust_get_model_files)
    set(IMPORT_LIST_FILE "${CMAKE_CURRENT_BINARY_DIR}/fpp-cache/stdout.txt")
    fprime_cmake_ASSERT("fpp-depend cache did not generate '${IMPORT_LIST_FILE}'" EXISTS "${IMPORT_LIST_FILE}")
    file(STRINGS "${IMPORT_LIST_FILE}" MODEL_FILES)
    set(FPRIME_RUST_MODEL_FILES "${MODEL_FILES}" PARENT_SCOPE)
endfunction(fprime_rust_get_model_files)

function(fprime_rust_is_supported AC_INPUT_FILE)
    autocoder_support_by_suffix(".fpp" "${AC_INPUT_FILE}" TRUE)
endfunction(fprime_rust_is_supported)

function(fprime_rust_setup_autocode MODULE_NAME AC_INPUT_FILES)
    find_program(FPRIME_RUST_AC NAMES fprime-rust-ac REQUIRED)
    fprime_cmake_ASSERT("'fprime-rust-ac' not found: pip install the fprime-rust package" NOT "${FPRIME_RUST_AC}" MATCHES ".*-NOTFOUND")
    if (TARGET "${FPRIME_GLOBAL_INTERFACE_TARGET}")
        get_property(FPRIME_BUILD_LOCATIONS TARGET "${FPRIME_GLOBAL_INTERFACE_TARGET}" PROPERTY FPRIME_LOCATIONS)
    endif()
    set(COMMON_ARGUMENTS "${CMAKE_CURRENT_BINARY_DIR}" "--output-directory" "${CMAKE_CURRENT_BINARY_DIR}"
        --prefixes ${FPRIME_BUILD_LOCATIONS} "--translation-units" ${AC_INPUT_FILES})
    execute_process(
        COMMAND "${FPRIME_RUST_AC}" "bindings" ${COMMON_ARGUMENTS} "--dry-run"
        OUTPUT_VARIABLE GENERATED_FILES_RAW
        ERROR_VARIABLE GENERATED_FILES_ERROR
        RESULT_VARIABLE GENERATED_FILES_RESULT
    )
    if (NOT GENERATED_FILES_RESULT EQUAL 0)
        message(FATAL_ERROR "[fprime_rust] fprime-rust-ac failed for ${MODULE_NAME}:\n${GENERATED_FILES_ERROR}")
    endif()
    string(REPLACE "\n" ";" GENERATED_FILES_LIST "${GENERATED_FILES_RAW}")
    list(FILTER GENERATED_FILES_LIST EXCLUDE REGEX "^$")
    set(GENERATED_BUILD_FILES "${GENERATED_FILES_LIST}")
    list(FILTER GENERATED_BUILD_FILES INCLUDE REGEX "^${CMAKE_CURRENT_BINARY_DIR}/")
    set(SEED_FILES "${GENERATED_FILES_LIST}")
    list(FILTER SEED_FILES EXCLUDE REGEX "^${CMAKE_CURRENT_BINARY_DIR}/")
    get_target_property(MODULE_TYPE ${MODULE_NAME} TYPE)
    if (GENERATED_BUILD_FILES AND NOT MODULE_TYPE STREQUAL "INTERFACE_LIBRARY")
        if (SEED_FILES)
            # The user's <Comp>.rs does not exist yet: seed it from the template now (REQ-FprimeRust-007)
            message(STATUS "[fprime_rust] Seeding ${SEED_FILES}")
            execute_process(COMMAND "${FPRIME_RUST_AC}" "bindings" ${COMMON_ARGUMENTS} COMMAND_ERROR_IS_FATAL ANY)
        endif()
        set(GENERATED_CPP_FILES "${GENERATED_BUILD_FILES}")
        set(GENERATED_HPP_FILES "${GENERATED_BUILD_FILES}")
        set(GENERATED_RS_FILES "${GENERATED_BUILD_FILES}")
        list(FILTER GENERATED_CPP_FILES INCLUDE REGEX "^.*\\.cpp$")
        list(FILTER GENERATED_HPP_FILES INCLUDE REGEX "^.*\\.hpp$")
        list(FILTER GENERATED_RS_FILES INCLUDE REGEX "^.*\\.rs$")
        execute_process(
            COMMAND "${FPRIME_RUST_AC}" "components" ${COMMON_ARGUMENTS}
            OUTPUT_VARIABLE COMPONENT_SPECS_RAW
            COMMAND_ERROR_IS_FATAL ANY
        )
        string(REPLACE "\n" ";" COMPONENT_SPECS "${COMPONENT_SPECS_RAW}")
        list(FILTER COMPONENT_SPECS EXCLUDE REGEX "^$")
        append_list_property("${COMPONENT_SPECS}" TARGET "${MODULE_NAME}" PROPERTY FPRIME_RUST_COMPONENTS)
        # The executable's Rust archive (its FPRIME_RUST_ARCHIVE property, set by target/fprime_rust) is linked
        # right after this module so the shim objects defining the helpers it references precede it
        target_link_libraries("${MODULE_NAME}" INTERFACE "$<TARGET_PROPERTY:FPRIME_RUST_ARCHIVE>" FprimeRust)
        fprime_rust_get_model_files()
        add_custom_command(
            OUTPUT ${GENERATED_BUILD_FILES}
            DEPENDS ${AC_INPUT_FILES} ${FPRIME_RUST_MODEL_FILES}
            COMMAND "${FPRIME_RUST_AC}" "bindings" ${COMMON_ARGUMENTS}
            COMMENT "[fprime_rust] Generating Rust bindings for ${MODULE_NAME}"
        )
        set(AUTOCODER_DEPENDENCIES "FprimeRust" PARENT_SCOPE)
        set(AUTOCODER_GENERATED_BUILD_SOURCES ${GENERATED_CPP_FILES} PARENT_SCOPE)
        set(AUTOCODER_GENERATED_OTHER ${GENERATED_HPP_FILES} ${GENERATED_RS_FILES} PARENT_SCOPE)
    else()
        set(AUTOCODER_DEPENDENCIES "" PARENT_SCOPE)
        set(AUTOCODER_GENERATED_BUILD_SOURCES "" PARENT_SCOPE)
        set(AUTOCODER_GENERATED_OTHER "" PARENT_SCOPE)
    endif()
endfunction(fprime_rust_setup_autocode)
