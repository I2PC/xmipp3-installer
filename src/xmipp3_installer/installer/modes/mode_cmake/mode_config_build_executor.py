from typing import Tuple, List, Optional, Union

from xmipp3_installer.application.logger import predefined_messages, errors
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.installer.handlers import shell_handler
from xmipp3_installer.installer.modes.mode_cmake import mode_cmake_executor
from xmipp3_installer.repository.config_vars import variables

class ModeConfigBuildExecutor(mode_cmake_executor.ModeCMakeExecutor):
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
    if shell_handler.run_shell_command_in_streaming(cmd, show_output=True, substitute=self.substitute):
      return errors.CMAKE_CONFIGURE_ERROR, ""
    return 0, ""
  
  def __get_cmake_vars(self) -> str:
    """
    ### Returns the CMake variables required for the configuration step.

    #### Returns:
    - (str): String containing all required CMake variables
    """
    return " ".join([
      f"-D{variable_key}={self.context[variable_key]}" for variable_key
      in self.__get_config_vars() if not self.__is_empty(self.context[variable_key])
    ])
  
  def __get_config_vars(self) -> List[str]:
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

  def __is_empty(self, value: Optional[Union[bool, str]]) -> bool:
    """
    ### Checks if the given config value is empty.

    #### Params:
    - value (bool | str | None): Value to be checked.

    #### Returns:
    - (bool): True if it is empty, False otherwise.
    """
    return value is None or value == ""
