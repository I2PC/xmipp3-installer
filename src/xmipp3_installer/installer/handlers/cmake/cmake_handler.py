"""### Functions that interact with CMake."""

from __future__ import annotations

import os
import shutil
from typing import Any

from xmipp3_installer.installer.handlers.cmake import cmake_constants


def get_cmake_path() -> str | None:
  """
  ### Returns the path to the CMake executable.

  #### Returns:
  - (str | None): Path to the CMake executable if found, None otherwise.
  """
  return shutil.which(cmake_constants.DEFAULT_CMAKE)

def get_cmake_params(variables: list[tuple[str, str | bool]]) -> str:
  """
  ### Converts the given list of variable names into CMake parameters.

  #### Params:
  - variables (list): List of variable names to obtain the parameters from.
  """
  result = []
  for key, value in variables:
    result.append(f"-D{key}={value}")
  return ' '.join(result)

def get_library_versions_from_cmake_file(path: str) -> dict[str, Any]:
  """
  ### Obtains the library versions from the CMake cache file.

  #### Params:
  - path (str): Path to the file containing all versions.

  #### Returns:
  - (dict(str, any)): Dictionary containing all the library versions in the file.
  """
  if not os.path.exists(path):
    return {}
  
  result = {}
  with open(path, encoding="utf-8") as versions_file:
    for line in versions_file:
      result.update(__get_library_version_from_line(line))
  return result

def __get_library_version_from_line(version_line: str) -> dict[str, Any]:
  """
  ### Retrieves the name and version of the library in the given line.
  
  #### Params:
  - version_line (str): Text line containing the name and version of the library.
  
  #### Returns:
  - (dict(str, any)): Dictionary where the key is the name and the value is the version.
  """
  TOKEN_NUMBER = 2 # Two tokens separated by a =
  library_with_version = {}
  name_and_version = version_line.replace("\n", "").split('=')
  if len(name_and_version) == TOKEN_NUMBER:
    version = name_and_version[1] if name_and_version[1] else None
    library_with_version[name_and_version[0]] = version
  return library_with_version
