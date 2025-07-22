"""
### Mode Config Build Executor Module.

This module contains the class to configure the build using CMake.
"""

from typing import List, Optional, Tuple, Union, cast

from xmipp3_installer.application.logger import errors, predefined_messages
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.installer.handlers import shell_handler
from xmipp3_installer.installer.handlers.cmake import cmake_handler
from xmipp3_installer.installer.modes.mode_cmake import mode_cmake_executor
from xmipp3_installer.repository.config_vars import variables

class ModeConfigBuildExecutor(mode_cmake_executor.ModeCMakeExecutor):
  """
  ### Mode Config Build Executor.

  Configures the build using CMake with the appropriate parameters.
  """
  
  def _run_cmake_mode(self, cmake: str) -> Tuple[int, str]:
    """
    ### Runs the CMake config with the appropiate params.

    #### Params:
    - cmake (str): Path to CMake executable.

    #### Returns:
    - (tuple(int, str)): Tuple containing the error status and an error message if there was an error. 
    """
    logger(predefined_messages.get_section_message("Configuring with CMake"))
    cmd = f"{cmake} -S . -B {paths.BUILD_PATH} -DCMAKE_BUILD_TYPE={self.build_type} {self.__get_cmake_vars()}"
    ret_code = shell_handler.run_shell_command_in_streaming(cmd, show_output=True, substitute=self.substitute)
    if ret_code:
      return self._get_error_code(ret_code, errors.CMAKE_CONFIGURE_ERROR), ""
    logger(predefined_messages.get_done_message(), substitute=self.substitute)
    return 0, ""
  
  def __get_cmake_vars(self) -> str:
    """
    ### Returns the CMake variables required for the configuration step.

    #### Returns:
    - (str): String containing all required CMake variables
    """
    non_empty_variables = [
      (
        variable_key,
        cast(Union[str, bool], self.context[variable_key])
      ) for variable_key in _get_non_internal_config_vars()
      if not _is_empty(self.context[variable_key])
    ]
    return cmake_handler.get_cmake_params(non_empty_variables)
  
def _get_non_internal_config_vars() -> List[str]:
  """
  ### Returns all non-internal config variable keys.

  #### Returns:
  - (list(str)): A list containing all non-internal config variable keys.
  """
  all_config_var_keys = [
    config_var for variable_section in variables.CONFIG_VARIABLES.values()
    for config_var in variable_section
  ]
  non_internal_keys = list(set(all_config_var_keys) - set(variables.INTERNAL_LOGIC_VARS))
  non_internal_keys.sort() # To keep order consistency
  return non_internal_keys

def _is_empty(value: Optional[Union[bool, str]]) -> bool:
  """
  ### Checks if the given config value is empty.

  #### Params:
  - value (bool | str | None): Value to be checked.

  #### Returns:
  - (bool): True if it is empty, False otherwise.
  """
  return not isinstance(value, bool) and not value
