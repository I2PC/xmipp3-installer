"""# Contains functions that interact with the configuration file."""

import os
from typing import List

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

