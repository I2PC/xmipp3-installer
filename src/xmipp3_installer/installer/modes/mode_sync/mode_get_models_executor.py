"""
### Mode Get Models Executor Module.

This module contains the class to download deep learning models.
"""

import os
from typing import Dict, Tuple

from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer import urls
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.installer.handlers import shell_handler
from xmipp3_installer.installer.modes.mode_sync.mode_sync_executor import ModeSyncExecutor

class ModeGetModelsExecutor(ModeSyncExecutor):
  """
  ### Mode Get Models Executor.

  Downloads deep learning models for the installation.
  """
  
  def __init__(self, context: Dict):
    """
    ### Constructor.
    
    #### Params:
    - context (dict): Dictionary containing the installation context variables.
    """
    super().__init__(context)
    self.models_directory = context.pop(params.PARAM_MODELS_DIRECTORY)
    if self.models_directory == os.path.abspath(paths.INSTALL_PATH):
      self.models_directory = os.path.join(self.models_directory, 'models')

  def _sync_operation(self) -> Tuple[int, str]:
    """
    ### Downloads deep learning models.

    #### Returns:
    - (tuple(int, str)): Tuple containing the return code and an error message if there was an error.
    """
    if os.path.isdir(self.models_directory):
      task = "update"
      in_progress_task = "Updating"
      completed_task = "updated"
    else:
      task = "download"
      in_progress_task = "Downloading"
      completed_task = "downloaded"
    
    logger(f"{in_progress_task} Deep Learning models (in background)")
    ret_code = shell_handler.run_shell_command_in_streaming(
      f"{self.sync_program_path} {task} {self.models_directory} {urls.MODELS_URL} DLmodels",
      show_output=True,
      show_error=True,
      substitute=True
    )
    if not ret_code:
      logger(logger.green(f"Models successfully {completed_task}!"))

    ret_code = 1 if ret_code else ret_code
    return ret_code, ""
