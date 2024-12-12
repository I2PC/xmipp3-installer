import sys
from typing import Dict

from xmipp3_installer.application.cli.arguments import modes
from xmipp3_installer.installer.modes import mode_selector
from xmipp3_installer.application.logger.logger import logger

def run_installer(args: Dict):
  mode = args.get(modes.MODE, modes.MODE_ALL)
  mode_executor = mode_selector.MODE_EXECUTORS[mode](args)
  ret_code, output = mode_executor.run()
  if ret_code:
    logger.log_error(output, ret_code=ret_code)
  # Else print done?
  sys.exit(mode_executor.run())
