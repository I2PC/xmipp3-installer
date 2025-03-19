"""
### Mode Version Executor Module.

This module contains the class to collect and display version information.
"""
import os
from typing import Dict, Tuple

from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.api_client.assembler import installation_info_assembler
from xmipp3_installer.installer import constants
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.installer.modes import mode_executor
from xmipp3_installer.installer.handlers import git_handler, versions_manager
from xmipp3_installer.installer.handlers.cmake import cmake_handler
from xmipp3_installer.repository.config_vars import variables

class ModeVersionExecutor(mode_executor.ModeExecutor):
  """
  ### Mode Version Executor.

  Collects and displays version information for the installation.
  """
  
  __LEFT_TEXT_LEN = 25

  def __init__(self, context: Dict):
    """
    ### Constructor.
    
    #### Params:
    - context (dict): Dictionary containing the installation context variables.
    """
    super().__init__(context)
    self.short = context.pop(params.PARAM_SHORT)
    config_exists = os.path.exists(paths.CONFIG_FILE)
    self.version_file_exists = os.path.exists(paths.LIBRARY_VERSIONS_FILE)
    self.is_configured = config_exists and self.version_file_exists
    versions: versions_manager.VersionsManager = context[constants.VERSIONS_CONTEXT_KEY]
    self.xmipp_version_number = versions.xmipp_version_number
    self.xmipp_version_name = versions.xmipp_version_name
    self.release_date = versions.xmipp_release_date
  
  def run(self) -> Tuple[int, str]:
    """
    ### Collects all the version information available and displays it.

    #### Returns:
    - (tuple(int, str)): Tuple containing the error status and an error message if there was an error.
    """
    installation_info =  self.xmipp_version_name if self.short else self.__get_long_version()
    logger(installation_info)
    return 0, ""

  def __get_long_version(self) -> str:
    """
    ### Returns the long version of the installation info.

    #### Returns:
    - (str): Long version of the installation info.
    """
    installation_info_lines = []
    version_type = 'release' if git_handler.is_tag() else git_handler.get_current_branch()
    title = f"Xmipp {self.xmipp_version_number} ({version_type})"
    installation_info_lines.append(f"{logger.bold(title)}\n")
    installation_info_lines.append(self.__get_dates_section())
    system_version_left_text = self.__add_padding_spaces("System version: ")
    installation_info_lines.append(f"{system_version_left_text}{installation_info_assembler.get_os_release_name()}")
    installation_info_lines.append(self.__get_sources_info())
    if self.version_file_exists:
      installation_info_lines.append(f"\n{self.__get_library_versions_section()}")
    if not self.is_configured or not _are_all_sources_present():
      installation_info_lines.append(f"\n{_get_configuration_warning_message()}")
    return '\n'.join(installation_info_lines)

  def __get_dates_section(self) -> str:
    """
    ### Returns the message section related to dates.

    #### Returns:
    - (str): Dates related message section.
    """
    dates_section = f"{self.__add_padding_spaces('Release date: ')}{self.release_date}\n"
    dates_section += f"{self.__add_padding_spaces('Compilation date: ')}"
    last_modified = self.context.get(variables.LAST_MODIFIED_KEY)
    dates_section += last_modified if last_modified else '-'
    return dates_section

  def __get_sources_info(self) -> str:
    """
    ### Returns the message section related to sources.

    #### Returns:
    - (str): Sources related message section.
    """
    sources_message_lines = []
    for source_package in constants.XMIPP_SOURCES:
      sources_message_lines.append(self.__get_source_info(source_package))
    return '\n'.join(sources_message_lines)

  def __get_source_info(self, source: str) -> str:
    """
    ### Returns the info message related to a given source.

    #### Params:
    - source (str): Source to get the message about.

    #### Returns:
    - (str): Info message about the given source.
    """
    source_path = paths.get_source_path(source)
    source_left_text = self.__add_padding_spaces(f"{source} branch: ")
    if not os.path.exists(source_path):
      return f"{source_left_text}{logger.yellow('Not found')}"
    current_commit = git_handler.get_current_commit(dir=source_path)
    commit_branch = git_handler.get_commit_branch(current_commit, dir=source_path)
    current_branch = git_handler.get_current_branch(dir=source_path)
    display_name = commit_branch if git_handler.is_tag(dir=source_path) else current_branch
    return f"{source_left_text}{display_name} ({current_commit})"

  def __add_padding_spaces(self, left_text: str) -> str:
    """
    ### Adds right padding as spaces to the given text until it reaches the desired length.

    #### Params:
    - left_text (str): Text to add padding to.

    #### Returns:
    - (str): Padded string.
    """
    text_len = len(left_text)
    if text_len >= self.__LEFT_TEXT_LEN:
      return left_text
    spaces = ''.join([' ' for _ in range(self.__LEFT_TEXT_LEN - text_len)])
    return f"{left_text}{spaces}"

  def __get_library_versions_section(self) -> str:
    """
    ### Retrieves the version of the libraries used in the project.
    
    #### Returns:
    - (str): Libraries with their version.
    """
    version_lines = [] 
    for library, version in cmake_handler.get_library_versions_from_cmake_file(
      paths.LIBRARY_VERSIONS_FILE
    ).items():
      library_left_text = self.__add_padding_spaces(f"{library}: ")
      version_lines.append(f"{library_left_text}{version}")
    return '\n'.join(version_lines)
  
def _are_all_sources_present() -> bool:
  """
  ### Check if all required source packages are present.

  #### Returns:
  - (bool): True if all source packages are present, False otherwise.
  """
  for source_package in paths.XMIPP_SOURCE_PATHS:
    if not os.path.exists(source_package):
      return False
  return True

def _get_configuration_warning_message() -> str:
  """
  ### Returns a message indicating configuration is not complete.

  #### Returns:
  - (str): 
  """
  return '\n'.join([
    logger.yellow("This project has not yet been configured, so some detectable dependencies have not been properly detected."),
    logger.yellow("Run mode 'getSources' and then 'configBuild' to be able to show all detectable ones.")
  ])
