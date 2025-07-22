"""### Functions that interact with CMake."""

import os
import shutil
from typing import Any, Dict, Optional, Tuple, Union, List

from xmipp3_installer.installer.handlers import shell_handler
from xmipp3_installer.installer.handlers.cmake import cmake_constants


def run_cmake_command(cmake: str, args: str, substitute: bool = True) -> int:
  """
  ### Runs a CMake command with the given arguments.

  #### Params:
  - cmake (str): Path to the CMake executable.
  - args (str): Arguments to pass to the CMake command.
  - substitute (bool): Whether to substitute variables in the command.

  #### Returns:
  - (int): Return code of the CMake command.
  """
  return 1
  #cmake = cmake if cmake else get_cmake_path()
  #cmd = f"{cmake} {args}"
  #return shell_handler.run_shell_command_in_streaming(cmd, show_output=True, substitute=substitute)

def get_cmake_path() -> Optional[str]:
  """
  ### Returns the path to the CMake executable.

  #### Returns:
  - (str | None): Path to the CMake executable if found, None otherwise.
  """
  return shutil.which(cmake_constants.DEFAULT_CMAKE)

def get_cmake_params(variables: List[Tuple[str, Union[str, bool]]]) -> str:
  """
  ### Converts the given list of variable names into CMake parameters.

  #### Params:
  - variables (list): List of variable names to obtain the parameters from.
  """
  result = []
  for key, value in variables:
    result.append(f"-D{key}={value}")
  return ' '.join(result)

def get_library_versions_from_cmake_file(path: str) -> Dict[str, Any]:
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
    for line in versions_file.readlines():
      result.update(__get_library_version_from_line(line))
  return result

def __get_library_version_from_line(version_line: str) -> Dict[str, Any]:
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
