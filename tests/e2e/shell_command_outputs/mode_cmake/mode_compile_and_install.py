import os
from unittest.mock import patch

from xmipp3_installer.application.logger import predefined_messages
from xmipp3_installer.installer import constants
from xmipp3_installer.installer.handlers import git_handler

from . import (
  get_predefined_error, get_project_subpath,
  CMAKE_EXECUTABLE
)

ERROR_TARGET_MESSAGE_START = "FAILED: CMakeFiles/build_error_target "
__INSTALLING_MESSAGE_LINE = "------------------- Installing with CMake ------------------"
BUILD_ERROR_TARGET_SUBPATH = os.path.join("build", "CMakeFiles", "build_error_target")

# Projects are installed inside a git repository on the main branch, see init_git_repository
with patch.object(git_handler, "is_tag", return_value=False), \
  patch.object(git_handler, "get_current_branch", return_value=constants.MAIN_BRANCHNAME):
  __SUCCESS_MESSAGE = predefined_messages.get_success_message("")

__COMMON_SECTION = f"""------------------- Compiling with CMake -------------------
{CMAKE_EXECUTABLE} --build build --config Release -j 1"""
__COMPILATION_SUCCESS = f"""{predefined_messages.get_done_message()}

{__INSTALLING_MESSAGE_LINE}
{CMAKE_EXECUTABLE} --install build --config Release"""

BUILD_FAILURE = f"""{__COMMON_SECTION}
[1/1] This command is expected to fail:
{ERROR_TARGET_MESSAGE_START}{get_project_subpath(BUILD_ERROR_TARGET_SUBPATH)}
{get_predefined_error(5, "compiling")}
"""

INSTALL_FAILURE = f"""{__COMMON_SECTION}
{__COMPILATION_SUCCESS}
{get_predefined_error(6, "installing")}
"""

SUCCESS = f"""{__COMMON_SECTION}
[1/1] This command is expected to succeed
{__COMPILATION_SUCCESS}
{predefined_messages.get_done_message()}
{__SUCCESS_MESSAGE}
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

def remove_command_error_line(raw_output: str) -> str: # Error line containing system-specific details
  splitted = raw_output.splitlines(keepends=True)
  new_output_lines = []
  for line in splitted:
    if "cd " in line: # It's the only line containig a directory change
      continue
    new_output_lines.append(line)
  return ''.join(new_output_lines)

def normalize_error_path(raw_output: str) -> str: # Absolute path changes per run
  path_index = raw_output.find(ERROR_TARGET_MESSAGE_START)
  if path_index == -1:
    return raw_output
  path_index += len(ERROR_TARGET_MESSAGE_START)
  text_up_to_path = raw_output[:path_index]
  next_line_index = raw_output.find("\n", path_index)
  build_error_target_path = get_project_subpath(BUILD_ERROR_TARGET_SUBPATH)
  return f"{text_up_to_path}{build_error_target_path}{raw_output[next_line_index:]}"

def normalize_line_breaks(raw_output: str) -> str: # The number of line breaks in CMake is OS dependant
  splitted = raw_output.splitlines()
  previous_line = None
  new_lines = []
  for line_index in range(len(splitted)):
    line = splitted[line_index]
    if not line:
      previous_line = line
      continue
    if (
      (line.startswith("------") and line_index != 0) or
      (line.startswith("**") and previous_line == "")
    ):
      line = f"\n{line}"
    previous_line = line
    new_lines.append(line)
  return "\n".join([*new_lines, ""])

def remove_ninja_error_code(raw_output: str) -> str:
  return raw_output.replace(" [code=1]", "")
