import json
import os
from io import TextIOWrapper
from typing import Dict

from xmipp3_installer.application.logger.logger import logger

VERSION_NUMBER_KEY = "version_number"
VERSION_NAME_KEY = "version_name"
RELEASE_DATE_KEY = "release_date"
SOURCES_KEY = "sources"
MIN_VERSION_KEY = "min_version"

def get_version_info(file_path: str, show_warnings: bool=True) -> Dict[str, str]:
  """
  ### Retrieves the version info from the version information JSON file.

  #### Params:
  - file_path (str): Path to the version JSON file.

  #### Returns:
  - (dict(str, str)): Dictionary containing the parsed values.
  """
  version_info = {}
  if not os.path.exists(file_path):
    return {}
  
  with open(file_path) as json_data:
    version_info = __read_json_from_file_data(json_data, show_warnings)

  return version_info

def __read_json_from_file_data(file_data: TextIOWrapper, show_warnings: bool) -> Dict[str, str]:
  """
  ### Reads a JSON file and returns its contents.

  #### Params:
  - file_data (TextIOWrapper): File data object.
  - show_warnings (bool): Whether to show warnings when the file cannot be read.

  #### Returns:
  - (dict(str, str)): Dictionary containing the parsed values.
  """
  try:
    return json.load(file_data)
  except UnicodeDecodeError as encoding_error:
    warning_message = f"WARNING: Version information is not encoded properly:\n{encoding_error}"
  except json.JSONDecodeError as json_error:
    warning_message = "WARNING: Version information is not in valid JSON format. "
    warning_message += f"See complete error below:\n{json_error}"
  if show_warnings:
    logger(logger.yellow(warning_message))
  return {}
