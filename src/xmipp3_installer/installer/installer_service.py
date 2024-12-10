import sys
from typing import Dict

from xmipp3_installer.application.cli.arguments import modes
from xmipp3_installer.installer.modes import mode_selector

def run_installer(args: Dict):
  mode = args.get(modes.MODE, modes.MODE_ALL)
  ret_code = bool(mode_selector.MODE_FUNCTIONS[mode](args)) # Ret code?
  sys.exit(ret_code)
