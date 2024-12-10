from typing import Dict

from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.repository import config

def mode_config(args: Dict) -> Dict:
  """
  ### Runs the installer's config mode

  #### Params:
  - args (dict): Dictionary containing all parsed command-line params.

  #### Returns:
  - (dict): Dictionary containing all config variables.
  """
  overwrite = args.get(params.PARAM_OVERWRITE, False)
  file_handler = config.ConfigurationFileHandler()
  file_handler.write_config(overwrite=overwrite)
  return file_handler.values
