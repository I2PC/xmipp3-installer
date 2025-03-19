"""
### Mode Git Executor Module.

This module contains the class to execute git commands on all Xmipp source repositories.
"""

from typing import Dict, Tuple

from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer import constants
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.installer.modes import mode_executor
from xmipp3_installer.installer.handlers import git_handler

class ModeGitExecutor(mode_executor.ModeExecutor):
  """
  ### Mode Git Executor.

  Executes git commands on all Xmipp source repositories.
  """

  def __init__(self, context: Dict):
    """
    ### Constructor.
    
    #### Params:
    - context (dict): Dictionary containing the installation context variables.
    """
    super().__init__(context)
    command_param_list = context.pop(params.PARAM_GIT_COMMAND)
    self.command = ' '.join(command_param_list)
  
  def run(self) -> Tuple[int, str]:
    """
    ### Executes the given git command into all xmipp source repositories.

    #### Returns:
    - (tuple(int, str)): Tuple containing the return code and an error message if there was an error.
    """
    logger(f"Running command 'git {self.command}' for all xmipp sources...")

    for source in [constants.XMIPP, *constants.XMIPP_SOURCES]:
      logger("\n" + logger.blue(
        f"Running command for {source} in path {paths.get_source_path(source)}..."
      ))
      ret_code, output = git_handler.execute_git_command_for_source(
        self.command, source
      )
      if ret_code:
        return ret_code, output

    return 0, ""
