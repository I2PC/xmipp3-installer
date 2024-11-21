"""# Contains functions that interact with the configuration file."""

import re
import os
from typing import List, Optional, Tuple, Dict

from xmipp3_installer.installer import constants
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.repository.config_vars import default_values
from xmipp3_installer.repository.invalid_config_line import InvalidConfigLineError

__COMMENT_ESCAPE = '#'
__ASSIGNMENT_SEPARATOR = '='
__LAST_MODIFIED_TEXT = "Config file automatically generated on"

def read_config(path: str) -> Dict[str, str]:
  """
	### Reads the config file and returns a dictionary with all the parsed variables.

	#### Params:
	- path (str): Path to the config file.
	
	#### Returns:
	- (dict): Dictionary containing all the variables found in the config file.
	"""
  file_lines = __get_file_content(path)
  result = {}
  for line_number, line in enumerate(file_lines):
    try:
      key_value_pair = __parse_config_line(line, line_number + 1)
    except InvalidConfigLineError as error:
      logger(str(error))
      return default_values.CONFIG_DEFAULT_VALUES
    if key_value_pair:
      key, value = key_value_pair
      result[key] = value
  return {**default_values.CONFIG_DEFAULT_VALUES, **result}

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
	- (tuple(str, str) | None): Tuple containing the read key-value pair if line contains valid data.

  #### Raises:
  - RuntimeError: Raised when a line has an invalid format and cannot be parsed.
	"""
  line_without_comments = line.split(__COMMENT_ESCAPE, maxsplit=2)[0].strip()
  if not line_without_comments:
    return None
  
  tokens = line_without_comments.split(__ASSIGNMENT_SEPARATOR, maxsplit=1)
  if len(tokens) != 2:
    raise InvalidConfigLineError(
      InvalidConfigLineError.generate_error_message(
        constants.CONFIG_FILE,
        line_number,
        line
      )
    )
  
  return tokens[0].strip(), tokens[1].strip()

def __make_config_line(key: str, value: str, default_value: str) -> str:
  """
	### Composes a config file line given a key-value pair to write.

	#### Params:
  - key (int): Name of the variable.
	- value (str): Value of the variable found in the config file.
  - default_value (str): Default value of the variable.
	
	#### Returns:
	- (str): String containing the appropiately formatted key-value pair.
	"""
  default_value = '' if default_value is None else default_value
  value = default_value if value is None else value
  return f"{key}{__ASSIGNMENT_SEPARATOR}{value}" if key else ""
