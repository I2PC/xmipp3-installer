"""
### Mode Compile And Install Executor Module.

This module contains the class to compile and install using CMake.
"""

from typing import Tuple, Dict

from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.application.logger import predefined_messages, errors
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.installer.handlers import shell_handler
from xmipp3_installer.installer.modes.mode_cmake import mode_cmake_executor

class ModeCompileAndInstallExecutor(mode_cmake_executor.ModeCMakeExecutor):
  """
  ### Mode Compile And Install Executor.

  Compiles and installs using CMake with the appropriate parameters.
  """
  
  def __init__(self, context: Dict):
    """
    ### Constructor.
    
    #### Params:
    - context (dict): Dictionary containing the installation context variables.
    """
    super().__init__(context)
    self.jobs = context[params.PARAM_JOBS]

  def _set_executor_config(self):
    """### Sets the specific executor params for this mode."""
    super()._set_executor_config()
    self.prints_banner_on_exit = True

  def _run_cmake_mode(self, cmake: str) -> Tuple[int, str]:
    """
    ### Runs the CMake compilation & installation with the appropiate params.

    #### Params:
    - cmake (str): Path to CMake executable.

    #### Returns:
    - (tuple(int, str)): Tuple containing the error status and an error message if there was an error. 
    """
    logger(predefined_messages.get_section_message("Compiling with CMake"))
    cmd = f"{cmake} --build {paths.BUILD_PATH} --config {self.build_type} -j {self.jobs}"
    ret_code = shell_handler.run_shell_command_in_streaming(cmd, show_output=True, substitute=self.substitute)
    if ret_code:
      return self._get_error_code(ret_code, errors.CMAKE_COMPILE_ERROR), ""
    logger(predefined_messages.get_done_message(), substitute=self.substitute)
    
    installation_section_message = predefined_messages.get_section_message("Installing with CMake")
    logger(f"\n{installation_section_message}")
    cmd = f"{cmake} --install {paths.BUILD_PATH} --config {self.build_type}"
    ret_code = shell_handler.run_shell_command_in_streaming(cmd, show_output=True, substitute=self.substitute)
    if ret_code:
      return self._get_error_code(ret_code, errors.CMAKE_INSTALL_ERROR), ""
    logger(predefined_messages.get_done_message(), substitute=self.substitute)
    return 0, ""
