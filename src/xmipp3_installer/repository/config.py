"""# Contains functions that interact with the configuration file."""

import re
import os
from datetime import datetime
from typing import List

__LAST_MODIFIED_TEXT = "Config file automatically generated on"

def get_config_date(path: str) -> str:
  """
  ### Obtains from the config file the date of its last modification.

  #### Params:
  - path (str): Path to the config file.

  #### Returns:
  - (str): Date in dd/mm/yyyy format.
  """
  config_lines = __get_file_content(path)
  for line in config_lines:
    if __LAST_MODIFIED_TEXT not in line:
      continue
    match = re.search(r'\d{4}-\d{2}-\d{2}', line)
    if match:
      return datetime.strptime(match.group(), '%Y-%m-%d').strftime('%d/%m/%Y')
  return ""

def __get_file_content(path: str) -> List[str]:
  """
  ### Reads the whole unparsed content of the given file.
  
  #### Params:
  - path (str): Path to the config file.

  #### Returns:
  - (list(str)): Content of the file, where each line is a string in the result list.
  """
  if not os.path.exists(path):
    return []
  lines = []
  with open(path, "r") as config_file:
    lines = config_file.readlines()
  return lines

