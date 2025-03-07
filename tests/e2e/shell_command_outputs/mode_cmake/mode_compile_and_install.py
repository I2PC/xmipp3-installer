import os

from xmipp3_installer.application.logger import predefined_messages

from . import (
  get_predefined_error, get_project_abs_subpath,
  BUILD_ERROR_PROJECT, CMAKE_EXECUTABLE
)

ERROR_TARGET_MESSAGE_START = "FAILED: CMakeFiles/build_error_target "
BUILD_ERROR_TARGET_SUBPATH = os.path.join("build", "CMakeFiles", "build_error_target")
INSTALLING_MESSAGE_LINE = "------------------- Installing with CMake ------------------"

__COMMON_SECTION = f"""------------------- Compiling with CMake -------------------
{CMAKE_EXECUTABLE} --build build --config Release -j 1"""
__COMPILATION_SUCCESS = f"""
{INSTALLING_MESSAGE_LINE}
{CMAKE_EXECUTABLE} --install build --config Release"""

BUILD_FAILURE = f"""{__COMMON_SECTION}
[1/1] This command is expected to fail:
{ERROR_TARGET_MESSAGE_START}{get_project_abs_subpath(BUILD_ERROR_PROJECT, BUILD_ERROR_TARGET_SUBPATH)}
{get_predefined_error(5, "compiling")}
"""

INSTALL_FAILURE = f"""{__COMMON_SECTION}
{__COMPILATION_SUCCESS}
{get_predefined_error(6, "installing")}
"""

SUCCESS = f"""{__COMMON_SECTION}
[1/1] This command is expected to succeed
{__COMPILATION_SUCCESS}
{predefined_messages.get_success_message("")}
"""

def remove_ninja_output(raw_output: str) -> str: # Ninja output is printed or not depending on OS
	new_lines = []
	for line in raw_output.splitlines(keepends=True):
		line_without_ends = line.replace("\n", "").replace("\r", "")
		if line_without_ends in [
      "ninja: build stopped: subcommand failed.",
      "ninja: no work to do."
    ]:
			continue
		new_lines.append(line)
	return "".join(new_lines)
