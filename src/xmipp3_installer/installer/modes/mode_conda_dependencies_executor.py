"""
### Mode Conda Dependencies Executor Module.

This module contains the class to install Xmipp's dependencies in the current Conda environment.
"""

from __future__ import annotations

import json

from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.application.logger import errors, predefined_messages
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.installer.handlers import (
  conda_handler,
  nvidia_handler,
  shell_handler,
)
from xmipp3_installer.installer.modes import mode_executor
from xmipp3_installer.repository.config_vars import variables

_ID_KEY = "id"
_FILE_KEY = "file"
_MIN_DRIVER_VERSION_KEY = "min_driver_version"


class ModeCondaDependenciesExecutor(mode_executor.ModeExecutor):
  """
  ### Mode Conda Dependencies Executor.

  Installs the Conda environment file defined by Xmipp that fits this system
  into the currently active Conda environment.
  """

  def __init__(self, context: dict):
    """
    ### Constructor.

    #### Params:
    - context (dict): Dictionary containing the installation context variables.
    """
    super().__init__(context)
    self.substitute = not context[params.PARAM_KEEP_OUTPUT]
    self.use_cuda = context[variables.CUDA]
    self.forced_environment_id = context[variables.CONDA_ENVIRONMENT]

  def run(self) -> tuple[int, str]:
    """
    ### Installs the appropriate Conda environment file into the current Conda environment.

    #### Returns:
    - (tuple(int, str)): Tuple containing the error status and an error message if there was an error.
    """
    logger(predefined_messages.get_section_message("Installing dependencies in Conda environment"))
    conda_executable = conda_handler.get_conda_executable()
    conda_prefix = conda_handler.get_conda_prefix_path()
    if not conda_executable or not conda_prefix:
      return errors.CONDA_DEPENDENCIES_ERROR, (
        "No active Conda environment found. Activate the environment where Xmipp's dependencies should be installed."
      )
    try:
      environments = _read_environments(paths.CONDA_ENVIRONMENTS_FILE)
    except (OSError, ValueError, KeyError, TypeError) as error:
      return errors.CONDA_DEPENDENCIES_ERROR, (
        f"Could not read Conda environments file '{paths.CONDA_ENVIRONMENTS_FILE}': {error}"
      )
    environment, error_message = self._select_environment(environments)
    if not environment:
      return errors.CONDA_DEPENDENCIES_ERROR, error_message
    logger(f"Installing environment '{environment[_ID_KEY]}' from {environment[_FILE_KEY]} into {conda_prefix}...")
    cmd = conda_handler.get_environment_update_command(conda_executable, conda_prefix, environment[_FILE_KEY])
    ret_code = shell_handler.run_shell_command_in_streaming(cmd, show_output=True, substitute=self.substitute)
    if ret_code:
      return errors.CONDA_DEPENDENCIES_ERROR, ""
    logger(predefined_messages.get_done_message(), substitute=self.substitute)
    return 0, ""

  def _select_environment(self, environments: list[dict[str, str]]) -> tuple[dict[str, str] | None, str]:
    """
    ### Selects the environment to install.

    Without CUDA, the fallback environment is selected.
    Otherwise, the forced environment if there is one, or the first one supported by the NVIDIA driver.

    #### Params:
    - environments (list(dict(str, str))): Available environments, ordered by preference.

    #### Returns:
    - (tuple(dict(str, str) | None, str)): Selected environment, or None and an error message if none fits.
    """
    if not self.use_cuda:
      logger("CUDA is disabled, selecting environment without CUDA.")
      return _get_fallback_environment(environments)
    if self.forced_environment_id:
      return _get_environment_by_id(environments, self.forced_environment_id)
    driver_version = nvidia_handler.get_driver_version()
    if not driver_version:
      logger(logger.yellow("Could not detect the NVIDIA driver, selecting environment without CUDA."))
      return _get_fallback_environment(environments)
    for environment in environments:
      min_driver_version = environment.get(_MIN_DRIVER_VERSION_KEY)
      if min_driver_version and nvidia_handler.is_driver_compatible(driver_version, min_driver_version):
        logger(f"NVIDIA driver {driver_version} supports environment '{environment[_ID_KEY]}'.")
        return environment, ""
    logger(logger.yellow(
      f"NVIDIA driver {driver_version} is too old for any CUDA environment, selecting environment without CUDA."
    ))
    return _get_fallback_environment(environments)

def _read_environments(environments_file: str) -> list[dict[str, str]]:
  """
  ### Reads the environments defined in the given Conda environments file.

  #### Params:
  - environments_file (str): Path to the Conda environments file.

  #### Returns:
  - (list(dict(str, str))): Defined environments, ordered by preference.
  """
  with open(environments_file, encoding="utf-8") as json_file:
    environments = json.load(json_file)["environments"]
  if any(_ID_KEY not in environment or _FILE_KEY not in environment for environment in environments):
    raise ValueError(f"every environment must define '{_ID_KEY}' and '{_FILE_KEY}'")
  for environment in environments:
    min_driver_version = environment.get(_MIN_DRIVER_VERSION_KEY)
    if min_driver_version is not None and not nvidia_handler.is_valid_driver_version(min_driver_version):
      raise ValueError(f"invalid {_MIN_DRIVER_VERSION_KEY} '{min_driver_version}' in environment '{environment[_ID_KEY]}'")
  return environments

def _get_environment_by_id(
  environments: list[dict[str, str]],
  environment_id: str
) -> tuple[dict[str, str] | None, str]:
  """
  ### Returns the environment with the given id.

  #### Params:
  - environments (list(dict(str, str))): Available environments.
  - environment_id (str): Id of the environment to find.

  #### Returns:
  - (tuple(dict(str, str) | None, str)): Found environment, or None and an error message if it does not exist.
  """
  for environment in environments:
    if environment[_ID_KEY] == environment_id:
      logger(f"Selecting environment '{environment_id}' set in {variables.CONDA_ENVIRONMENT}.")
      return environment, ""
  available_ids = ", ".join(environment[_ID_KEY] for environment in environments)
  return None, (
    f"Conda environment '{environment_id}' set in {variables.CONDA_ENVIRONMENT} does not exist. "
    f"Available environments: {available_ids}."
  )

def _get_fallback_environment(environments: list[dict[str, str]]) -> tuple[dict[str, str] | None, str]:
  """
  ### Returns the environment that does not require any NVIDIA driver.

  #### Params:
  - environments (list(dict(str, str))): Available environments.

  #### Returns:
  - (tuple(dict(str, str) | None, str)): Fallback environment, or None and an error message if there is none.
  """
  for environment in environments:
    if not environment.get(_MIN_DRIVER_VERSION_KEY):
      return environment, ""
  return None, "There is no Conda environment without CUDA defined for this system."
