import os
import shutil

from xmipp3_installer.application.logger.logger import logger

from .. import XMIPP_DOCS
from .... import get_test_file

CMAKE_EXECUTABLE = "cmake"
TEST_CONFIG_FILE_PATH = get_test_file(os.path.join("conf-files", "input", "all-off.conf"))
VALID_PROJECT = "valid"
CONFIG_ERROR_PROJECT = "config_error"
BUILD_ERROR_PROJECT = "build_error"
INSTALL_ERROR_PROJECT = "install_error"
ENV = {**os.environ, "CMAKE_GENERATOR": "Ninja"}
PROJECT_PATH = "<project path>" # Each project is copied to a temporary path, replaced by this in outputs

def get_project_subpath(*subpaths: str) -> str:
  """
  ### Returns the given CMake project's subpath, as shown in normalized outputs.

  #### Params:
  - subpaths: (tuple(str)): All the separated (by "/") parts of the subpath.

  #### Returns:
  - (str): Subpath under the project path placeholder.
  """
  return os.path.join(PROJECT_PATH, *subpaths)

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
