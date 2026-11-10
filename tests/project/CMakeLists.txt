# Shim/build fixture project of fprime-rust (UT-SHIM-*, UT-BUILD-*): `fprime-util generate --ut && fprime-util check`
cmake_minimum_required(VERSION 3.24.2)
project(FprimeRustFixtures C CXX)
include("${FPRIME_FRAMEWORK_PATH}/cmake/FPrime.cmake")
include(FprimeRust)
fprime_setup_included_code()
add_fprime_subdirectory("${CMAKE_CURRENT_LIST_DIR}/Fixtures")
