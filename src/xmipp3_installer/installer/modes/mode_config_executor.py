"""
### Mode Config Executor Module.

This module contains the class to manage the configuration file.
"""

import os
from typing import Dict, Tuple

from xmipp3_installer.application.logger import errors
from xmipp3_installer.application.logger import predefined_messages
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.installer.modes import mode_executor
from xmipp3_installer.repository import config

class ModeConfigExecutor(mode_executor.ModeExecutor):
  """
  ### Mode Config Executor.

  Manages the configuration file for the installation.
  """

  def __init__(self, context: Dict):
    """
    ### Constructor.
    
    #### Params:
    - context (dict): Dictionary containing the installation context variables.
    """
    super().__init__(context)
    self.overwrite = context.pop(params.PARAM_OVERWRITE)
    self.config_values = {}
  
  def run(self) -> Tuple[int, str]:
    """
    ### Reads the config file and writes to it formatting properly with the appropiate values.

    #### Returns:
    - (tuple(int, str)): Tuple containing the error status and an error message if there was an error. 
    """
    logger(predefined_messages.get_section_message("Managing config file"))
    action_message = (
      "Generating config file from scratch with default values..."
      if self.overwrite or not os.path.exists(paths.CONFIG_FILE) else
      "Reading config file..."
    )
    logger(action_message)
    try:
      file_handler = config.ConfigurationFileHandler()
      file_handler.write_config(overwrite=self.overwrite)
    except PermissionError as permission_error:
      return errors.IO_ERROR, str(permission_error)
    self.config_values = file_handler.values
    logger(predefined_messages.get_done_message())
    return 0, ""
