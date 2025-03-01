# Usage:
# cmake . -B build/ # Should succeed
# cmake --build build/ # Should succeed
# cmake --install build/ # Should fail

cmake_minimum_required(VERSION 3.12)

project(install_error)

install(CODE "message(FATAL_ERROR \"This is expected to fail here\")")
