from typing import Dict

from xmipp3_installer.api_client import api_client
from xmipp3_installer.api_client.assembler import installation_info_assembler
from xmipp3_installer.application.cli.arguments import modes
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer import constants
from xmipp3_installer.installer.modes.mode_executor import ModeExecutor
from xmipp3_installer.application.logger import predefined_messages
from xmipp3_installer.installer.modes import mode_selector
from xmipp3_installer.repository.config import ConfigurationFileHandler


class InstallationManager:
  def __init__(self, args: Dict):
    self.args = args
    self.mode = args.get(modes.MODE, modes.MODE_ALL)
    self.mode_executor: ModeExecutor = mode_selector.MODE_EXECUTORS[self.mode](args)
    self.config_handler = ConfigurationFileHandler(path=constants.CONFIG_FILE)

  def run_installer(self):
    """
    ### Runs the installer with the given arguments.

    #### Returns:
    - (int): Return code.
    """
    ret_code, output = self.mode_executor.run()
    if ret_code:
      logger.log_error(output, ret_code=ret_code)
    if self.mode_executor.sends_installation_info:
      logger("Sending anonymous installation info...")
      api_client.send_installation_attempt(
        installation_info_assembler.get_installation_info(ret_code=ret_code)
      )
    if not ret_code and self.mode_executor.prints_banner_on_exit:
      logger(predefined_messages.get_success_message())
    return ret_code
