"""### Functions that interact with the NVIDIA driver via shell."""

from __future__ import annotations

import re

from xmipp3_installer.installer.handlers import shell_handler

_DRIVER_VERSION_REGEX = re.compile(r"^\d+(\.\d+)*$")


def get_driver_version() -> str | None:
  """
  ### Returns the version of the installed NVIDIA driver.

  #### Returns:
  - (str | None): Driver version, or None if it could not be obtained.
  """
  ret_code, output = shell_handler.run_shell_command(
    "nvidia-smi --query-gpu=driver_version --format=csv,noheader"
  )
  if ret_code or not output:
    return None
  driver_version = output.splitlines()[0].strip() # One line per GPU, all with the same driver
  return driver_version if is_valid_driver_version(driver_version) else None

def is_valid_driver_version(driver_version: object) -> bool:
  """
  ### Checks if the given value is a well-formed driver version.

  #### Params:
  - driver_version (object): Value to check.

  #### Returns:
  - (bool): True if it is a string of dot-separated numbers, False otherwise.
  """
  return isinstance(driver_version, str) and bool(_DRIVER_VERSION_REGEX.match(driver_version))

def is_driver_compatible(driver_version: str, min_driver_version: str) -> bool:
  """
  ### Checks if the given driver version is at least the minimum required.

  #### Params:
  - driver_version (str): Installed driver version.
  - min_driver_version (str): Minimum required driver version.

  #### Returns:
  - (bool): True if the driver version is greater than or equal to the minimum, False otherwise.
  """
  return _get_version_numbers(driver_version) >= _get_version_numbers(min_driver_version)

def _get_version_numbers(version: str) -> tuple[int, ...]:
  """
  ### Returns the numeric parts of a dot-separated version.

  #### Params:
  - version (str): Dot-separated version.

  #### Returns:
  - (tuple(int, ...)): Numeric parts of the version.
  """
  return tuple(int(part) for part in version.split("."))
