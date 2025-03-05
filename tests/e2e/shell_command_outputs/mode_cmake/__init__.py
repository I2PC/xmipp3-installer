import os

from ... import get_cmake_project_path
from .... import get_test_file

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

CMAKE_EXECUTABLE = "cmake"
TEST_CONFIG_FILE_PATH = get_test_file(os.path.join("conf-files", "input", "all-off.conf"))
VALID_PROJECT = "valid"
CONFIG_ERROR_PROJECT = "config_error"
BUILD_ERROR_PROJECT = "build_error"
INSTALL_ERROR_PROJECT = "install_error"
