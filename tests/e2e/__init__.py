import os

from .. import get_test_file

def get_cmake_project_path(project_name: str) -> str:
  """
  ### Returns the full path for the given CMake project name.

  #### Params:
  - project_name (str): Name of the project.

  #### Returns:
  - (str): CMake project path.
  """
  return os.path.abspath(
    get_test_file(
      os.path.join(
        "cmake-cases",
        project_name
      )
    )
  )
