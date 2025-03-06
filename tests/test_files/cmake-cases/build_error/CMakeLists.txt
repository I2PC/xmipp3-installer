# Usage:
# cmake . -B build/ # Should succeed
# cmake --build build/ # Should fail

cmake_minimum_required(VERSION 3.12)

project(build_error NONE)

add_custom_target(
    build_error_target ALL
    ${CMAKE_COMMAND} -E false
    COMMENT "This command is expected to fail:"
)
