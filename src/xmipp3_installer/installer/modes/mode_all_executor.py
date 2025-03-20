"""
### Mode All Executor Module.

This module contains the class to run the whole installation process.
"""

from typing import Tuple, Dict

from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer.modes import (
  mode_executor, mode_config_executor, mode_get_sources_executor
)
from xmipp3_installer.installer.modes.mode_cmake import (
  mode_config_build_executor, mode_compile_and_install_executor
)

class ModeAllExecutor(mode_executor.ModeExecutor):
  """
  ### Mode All Executor.

  Runs the whole installation process with the appropriate parameters.
  """
  
  def __init__(self, context: Dict):
    """
    ### Constructor.
    
    #### Params:
    - context (dict): Dictionary containing the installation context variables.
    """
    config_executor = mode_config_executor.ModeConfigExecutor(
      {**context, params.PARAM_OVERWRITE: False}
    )
    get_sources_executor = mode_get_sources_executor.ModeGetSourcesExecutor(
      context
    )
    config_build_executor = mode_config_build_executor.ModeConfigBuildExecutor(
      context
    )
    compile_and_install_executor = mode_compile_and_install_executor.ModeCompileAndInstallExecutor(
      context
    )
    self.executors = [
      config_executor,
      get_sources_executor,
      config_build_executor,
      compile_and_install_executor
    ]
    super().__init__(context)

  def _set_executor_config(self):
    """### Sets the specific executor params for this mode."""
    super()._set_executor_config()
    self.logs_to_file = True
    self.prints_with_substitution = True
    self.prints_banner_on_exit = True
    self.sends_installation_info = True

  def run(self) -> Tuple[int, str]:
    """
    ### Runs the whole installation process with the appropiate params.

    #### Returns:
    - (tuple(int, str)): Tuple containing the error status and an error message if there was an error. 
    """
    for executor_index in range(len(self.executors)):
      if executor_index != 0:
        logger("")
      ret_code, output = self.executors[executor_index].run()
      if ret_code:
        return ret_code, output
    return 0, ""
