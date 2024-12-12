import sys
from typing import Dict

from xmipp3_installer.application.cli.arguments import modes
from xmipp3_installer.installer.modes import mode_selector

def run_installer(args: Dict):
  mode = args.get(modes.MODE, modes.MODE_ALL)
  mode_executor = mode_selector.MODE_EXECUTORS[mode](args)
  sys.exit(mode_executor.run())
