"""
### Installer Service Module.

This module contains the class to manage the installation process.
"""

from typing import Dict, cast

from xmipp3_installer.api_client import api_client
from xmipp3_installer.api_client.assembler import installation_info_assembler
from xmipp3_installer.application.cli.arguments import modes
from xmipp3_installer.application.logger import errors
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer import constants
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.installer.handlers import versions_manager
from xmipp3_installer.installer.modes.mode_executor import ModeExecutor
from xmipp3_installer.application.logger import predefined_messages
from xmipp3_installer.installer.modes import mode_selector
from xmipp3_installer.repository import config
from xmipp3_installer.repository.config_vars import variables

class InstallationManager:
  """
  ### Installation Manager.

  Manages the installation process by executing the appropriate mode based on the given arguments.
  """
  
  def __init__(self, args: Dict):
    """
    ### Constructor.
		
    #### Params:
    - args (dict): Dictionary containing all parsed command-line arguments.
    """
    self.mode = args.pop(modes.MODE, modes.MODE_ALL)
    config_handler = config.ConfigurationFileHandler(path=paths.CONFIG_FILE, show_errors=False)
    self.context = {
      **args,
      **config_handler.values,
      variables.LAST_MODIFIED_KEY: config_handler.last_modified,
      constants.VERSIONS_CONTEXT_KEY: versions_manager.VersionsManager(paths.VERSION_INFO_FILE)
    }
    self.mode_executor: ModeExecutor = mode_selector.MODE_EXECUTORS[self.mode](self.context)

  def run_installer(self):
    """
    ### Runs the installer with the given arguments.

    #### Returns:
    - (int): Return code.
    """
    try:
      ret_code, output = self.mode_executor.run()
    except KeyboardInterrupt:
      logger.log_error("", ret_code=errors.INTERRUPTED_ERROR, add_portal_link=False)
      return errors.INTERRUPTED_ERROR
    if ret_code:
      logger.log_error(output, ret_code=ret_code, add_portal_link=ret_code != errors.INTERRUPTED_ERROR)
    if (
      self.mode_executor.sends_installation_info and 
      self.context[variables.SEND_INSTALLATION_STATISTICS]
    ):
      logger("Sending anonymous installation info...", show_in_terminal=False)
      api_client.send_installation_attempt(
        installation_info_assembler.get_installation_info(
          self.context[constants.VERSIONS_CONTEXT_KEY],
          ret_code=ret_code
        )
      )
    if not ret_code and self.mode_executor.prints_banner_on_exit:
      logger(predefined_messages.get_success_message(
        cast(
          versions_manager.VersionsManager,
          self.context[constants.VERSIONS_CONTEXT_KEY]
        ).xmipp_version_name
      ))
    logger.close()
    return ret_code
