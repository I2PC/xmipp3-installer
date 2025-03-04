import os

from .. import TEST_FILES_DIR

def get_cmake_project_path(project_name: str) -> str:
  """
  ### Returns the full path for the given CMake project name.

  #### Params:
  - project_name (str): Name of the project.

  #### Returns:
  - (str): CMake project path.
  """
  return os.path.abspath(
    os.path.join(
      TEST_FILES_DIR,
      "cmake-cases",
      project_name
    )
  )
get_cmake_project_path("") # TODO: Remove
