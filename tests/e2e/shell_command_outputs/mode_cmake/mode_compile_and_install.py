import os

from xmipp3_installer.application.logger import predefined_messages

from . import (
  get_predefined_error, get_project_abs_subpath,
  BUILD_ERROR_PROJECT, CMAKE_EXECUTABLE
)

ERROR_TARGET_MESSAGE_START = "FAILED: CMakeFiles/build_error_target "
BUILD_ERROR_TARGET_SUBPATH = os.path.join("build", "CMakeFiles", "build_error_target")

__COMMON_SECTION = f"""------------------- Compiling with CMake -------------------
{CMAKE_EXECUTABLE} --build build --config Release -j 1"""
__COMPILATION_SUCCESS = f"""
------------------- Installing with CMake ------------------
{CMAKE_EXECUTABLE} --install build --config Release"""

BUILD_FAILURE = f"""{__COMMON_SECTION}
[1/1] This command is expected to fail:

{ERROR_TARGET_MESSAGE_START}{get_project_abs_subpath(BUILD_ERROR_PROJECT, BUILD_ERROR_TARGET_SUBPATH)}

ninja: build stopped: subcommand failed.

{get_predefined_error(5, "compiling")}
"""

INSTALL_FAILURE = f"""{__COMMON_SECTION}
ninja: no work to do.
{__COMPILATION_SUCCESS}
{get_predefined_error(6, "installing")}
"""

SUCCESS = f"""{__COMMON_SECTION}
[1/1] This command is expected to succeed
{__COMPILATION_SUCCESS}
{predefined_messages.get_success_message("")}
"""
