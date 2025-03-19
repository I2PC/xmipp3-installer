"""### Contains functions that can interact with packages via shell with a generic interface."""

from typing import Optional

from xmipp3_installer.installer.handlers import shell_handler

def get_package_version(package_name: str) -> Optional[str]:
  """
  ### Retrieves the version of a package or program by executing '[package_name] --version' command.

  Params:
  - package_name (str): Name of the package or program.

  Returns:
  - (str | None): Version information of the package or None if not found or errors happened.
  """
  ret_code, output = shell_handler.run_shell_command(f'{package_name} --version')
  return output if ret_code == 0 else None
