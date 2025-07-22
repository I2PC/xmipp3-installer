"""
### Configuration Values Adapter Module.

This module contains functions to convert configuration values between file format and context format.
"""

from typing import Dict, Union

from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.repository.config_vars import variables, default_values

def get_context_values_from_file_values(file_values: Dict[str, str], show_warnings: bool=True) -> Dict[str, Union[str, bool]]:
  """
  ### Converts configuration values from file format to context format.
  
  Processes a dictionary of configuration values read from file, converting toggle values 
  from string ('ON'/'OFF') to boolean representation for use in the application context.

  #### Params:
  - file_values (dict(str, str)): Dictionary of configuration values as read from file.
  - show_warnings (bool): Optional. If True, warning messages are shown when applicable.

  #### Returns:
  - (dict(str, str | bool)): Dictionary with values converted to their context format.
  """
  context_values = {}
  for key, value in file_values.items():
    context_values[key] = __get_context_value_from_file_value(key, value, show_warnings)
  return context_values

def get_file_values_from_context_values(context_values: Dict[str, Union[str, bool]]) -> Dict[str, str]:
  """
  ### Converts configuration values from context format to file format.
  
  Processes a dictionary of configuration values from the application context, converting toggle values 
  from boolean to string ('ON'/'OFF') representation for storage in configuration file.

  #### Params:
  - context_values (dict(str, str | bool)): Dictionary of configuration values from context.

  #### Returns:
  - (dict(str, str)): Dictionary with values converted to their file storage format.
  """
  file_values = {}
  for key, value in context_values.items():
    file_values[key] = __get_file_value_from_context_value(key, value)
  return file_values

def __get_context_value_from_file_value(key: str, value: str, show_warnings: bool) -> Union[str, bool]:
  """
  ### Converts a single configuration value from file format to context format.

  #### Params:
  - key (str): Configuration variable key.
  - value (str): Value as read from file.
  - show_warnings (bool): Optional. If True, warning messages are shown when applicable.

  #### Returns:
  - (str | bool): Value converted to its context format.
  """
  if key in variables.CONFIG_VARIABLES[variables.TOGGLES]:
    return __get_boolean_value_from_string(key, value, show_warnings)
  return value

def __get_file_value_from_context_value(key: str, value: Union[str, bool]) -> Union[str, bool]:
  """
  ### Converts a single configuration value from context format to file format.

  #### Params:
  - key (str): Configuration variable key.
  - value (str | bool): Value from context.

  #### Returns:
  - (str): Value converted to its file storage format.
  """
  if key in variables.CONFIG_VARIABLES[variables.TOGGLES]:
    return __get_string_value_from_boolean(bool(value))
  return value

def __get_boolean_value_from_string(key: str, value: str, show_warning: bool) -> bool:
  """
  ### Converts a toggle value from string ('ON'/'OFF') to boolean.

  #### Params:
  - key (str): Configuration variable key.
  - value (str): String value to convert ('ON' or 'OFF').
  - show_warnings (bool): Optional. If True, warning message is shown when applicable.

  #### Returns:
  - (bool): Boolean representation of the toggle value.
  """
  if value not in {default_values.ON, default_values.OFF}:
    default_value = default_values.CONFIG_DEFAULT_VALUES[key]
    if show_warning:
      logger(logger.yellow(
        f"WARNING: config variable '{key}' has unrecognized value '{value}'. "
        f"Toggle values must be either '{default_values.ON}' or '{default_values.OFF}'. "
        f"Default value '{default_value}' will be used instead."
      ))
    value = default_value
  return value == default_values.ON

def __get_string_value_from_boolean(value: bool) -> str:
  """
  ### Converts a toggle value from boolean to string ('ON'/'OFF').

  #### Params:
  - value (bool): Boolean value to convert.

  #### Returns:
  - (str): String representation of the toggle value ('ON' or 'OFF').
  """
  return default_values.ON if value else default_values.OFF
