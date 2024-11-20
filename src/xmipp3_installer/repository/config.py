"""# Contains functions that interact with the configuration file."""

import re
import os
from typing import List, Optional, Tuple

__COMMENT_ESCAPE = '#'
__ASSIGNMENT_SEPARATOR = '='
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
    match = re.search(r'\d{2}/\d{2}/\d{4}', line)
    if match:
      return match.group()
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

def __parse_config_line(line: str, line_number: int) -> Optional[Tuple[str, str]]:
  """
	### Reads the given line from the config file and returns the key-value pair as a tuple.

	#### Params:
  - line_number (int): Line number inside the config file.
	- line (str): Line to parse.
	
	#### Returns:
	- (tuple(str, str)): Tuple containing the read key-value pair.
	"""
  line_without_comments = line.split(__COMMENT_ESCAPE, maxsplit=2)[0].strip()
  if not line_without_comments:
    return None
  
  tokens = line_without_comments.split(__ASSIGNMENT_SEPARATOR, maxsplit=1)
  if len(tokens) != 2:
    raise RuntimeError(f'Unable to parse line {line_number + 1}: {line}')
  
  return tokens[0].strip(), tokens[1].strip()
