import sys
from typing import Dict

from xmipp3_installer.api_client import api_client
from xmipp3_installer.api_client.assembler import installation_info_assembler
from xmipp3_installer.application.cli.arguments import modes
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer.modes.mode_executor import ModeExecutor
from xmipp3_installer.application.logger import predefined_messages
from xmipp3_installer.installer.modes import mode_selector


def run_installer(args: Dict):
  mode = args.get(modes.MODE, modes.MODE_ALL)
  mode_executor: ModeExecutor = mode_selector.MODE_EXECUTORS[mode](args)
  ret_code, output = mode_executor.run()
  if ret_code:
    logger.log_error(output, ret_code=ret_code)
  if mode_executor.sends_installation_info:
    logger("Sending anonymous installation info...")
    api_client.send_installation_attempt(
      installation_info_assembler.get_installation_info(ret_code=ret_code)
    )
  if not ret_code and mode_executor.prints_banner_on_exit:
    logger(predefined_messages.get_success_message())
  sys.exit(ret_code)
