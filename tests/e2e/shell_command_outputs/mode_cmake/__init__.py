import os
import shutil

from xmipp3_installer.application.logger.logger import logger

from .. import XMIPP_DOCS
from ... import get_cmake_project_path
from .... import get_test_file

CMAKE_EXECUTABLE = "cmake"
TEST_CONFIG_FILE_PATH = get_test_file(os.path.join("conf-files", "input", "all-off.conf"))
VALID_PROJECT = "valid"
CONFIG_ERROR_PROJECT = "config_error"
BUILD_ERROR_PROJECT = "build_error"
INSTALL_ERROR_PROJECT = "install_error"
ENV = {**os.environ, "CMAKE_GENERATOR": "Ninja"}
EXECUTION_TIME = "X.Y"

def get_project_abs_subpath(project_name: str, *subpaths: str) -> str:
  """
  ### Returns the absolute path for a given CMake project's subpath.

  #### Params:
  - project_name (str): Name of the CMake project.
  - subpaths: (tuple(str)): All the separated (by "/") parts of the subpath.

  #### Returns:
  - (str): Full absolute path to the given subpath.
  """
  return os.path.abspath(
    get_cmake_project_path(
      os.path.join(
        project_name,
        *subpaths
      )
    )
  )

def get_predefined_error(code: int, action: str) -> str:
  """
  ### Returns the predefined error message of a CMake error.

  #### Params:
  - code (int): Error code.
  - action (str): CMake failed action.

  #### Returns:
  - (str): Full error message.
  """
  return logger.red("\n".join([
    f"Error {code}: Error {action} with CMake.",
    "Check the inside file 'compilation.log'.",
    XMIPP_DOCS
  ]))

def normalize_cmake_executable(raw_output: str) -> str: # CMake used deppends on user's installation
	return raw_output.replace(shutil.which("cmake"), CMAKE_EXECUTABLE)
