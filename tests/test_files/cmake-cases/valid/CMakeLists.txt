# Usage:
# cmake . -B build/ # Should succeed
# cmake --build build/ # Should succeed
# cmake --install build/ # Should succeed

cmake_minimum_required(VERSION 3.12)

project(valid NONE)

add_custom_target(
    valid_target ALL
    ${CMAKE_COMMAND} -E true
    COMMENT "This command is expected to succeed"
)

install(CODE "message(\"This command is also expected to succeed\")")
