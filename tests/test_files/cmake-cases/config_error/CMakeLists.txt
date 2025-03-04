# Usage:
# cmake . -B build/ # Should fail

cmake_minimum_required(VERSION 3.12)

project(config_error NONE)

message(FATAL_ERROR "This CMakeLists.txt is expected to fail here")
