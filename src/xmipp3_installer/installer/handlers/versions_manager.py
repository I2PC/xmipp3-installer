"""
### Versions Manager Module.

This module contains the class to manage version information.
"""

import json
from datetime import datetime
from typing import Dict, List

from xmipp3_installer.installer import constants
from xmipp3_installer.shared import singleton

class VersionsManager(singleton.Singleton):
  """
  ### Versions Manager.

  Manages version information by reading and validating version data from a JSON file.
  """

  def __init__(self, version_file_path: str):
    """
    ### Constructor.
    
    Initializes the version manager by reading and validating version information from a JSON file.

    #### Params:
    - version_file_path (str): Path to the JSON file containing version information.

    #### Raises:
    - ValueError: If version numbers don't follow semver format (x.y.z) or release date isn't dd/mm/yyyy.
    """
    super().__init__()
    self.version_file_path = version_file_path
    version_info = self.__get_version_info()
    self.xmipp_version_number = version_info[constants.XMIPP]["version_number"]
    self.xmipp_version_name = version_info[constants.XMIPP]["version_name"]
    self.xmipp_release_date = version_info[constants.XMIPP]["release_date"]
    self.sources_versions = version_info["sources_target_tag"]
    self.__validate_fields()

  def __get_version_info(self) -> Dict[str, Dict[str, str]]:
    """
    ### Retrieves the version info from the version information JSON file.

    #### Returns:
    - (dict(str, dict(str, str))): Dictionary containing the parsed values.
    """
    with open(self.version_file_path, encoding="utf-8") as json_data:
      version_info = json.load(json_data)
    return version_info
  
  def __validate_fields(self):
    """
    ### Validates version numbers and release date format.
    
    Checks that:
    - Version numbers follow semantic versioning (x.y.z)
    - Release date follows dd/mm/yyyy format

    #### Raises:
    - ValueError: If any field doesn't match its required format.
    """
    self.__validate_version_number()
    self.__validate_release_date()

  def __validate_version_number(self):
    """
    ### Validates that version numbers follow semantic versioning format.
    
    Checks that version numbers are in x.y.z format where x, y, z are integers.

    #### Raises:
    - ValueError: If any version number doesn't follow the required format.
    """
    parts = self.xmipp_version_number.split('.')
    if not VersionsManager.__is_valid_semver(parts):
      raise ValueError(
        f"Version number '{self.xmipp_version_number}' is invalid. Must be three numbers separated by dots (x.y.z)."
      )

  @staticmethod
  def __is_valid_semver(version_parts: List[str]) -> bool:
    """
    ### Checks if version parts constitute a valid semantic version.
    
    #### Params:
    - version_parts (list(str)): List of strings representing version number parts.

    #### Returns:
    - (bool): True if version follows semver format, False otherwise.
    """
    SEMVER_N_NUMBERS = 3 # 3 numbers separated by dots: X.Y.Z
    return len(version_parts) == SEMVER_N_NUMBERS and all(part.isdigit() for part in version_parts)

  def __validate_release_date(self):
    """
    ### Validates that release date follows dd/mm/yyyy format.
    
    Checks that:
    - Date string follows dd/mm/yyyy format
    - Date is a valid calendar date

    #### Raises:
    - ValueError: If release date doesn't follow the required format or is invalid.
    """
    try:
      datetime.strptime(self.xmipp_release_date, "%d/%m/%Y")
    except ValueError:
      raise ValueError(
        f"Release date '{self.xmipp_release_date}' is invalid. Must be in dd/mm/yyyy format."
      )
