"""
### Mode Clean All Executor Module.

This module contains the class to clean all content from source and build directories.
"""

from typing import List

from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer import constants
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.installer.modes.mode_clean import mode_clean_executor

class ModeCleanAllExecutor(mode_clean_executor.ModeCleanExecutor):
  """
  ### Mode Clean All Executor.

  Cleans all content from source and build directories.
  """

  @property
  def confirmation_keyword(self) -> str:
    """### Property containineg the keyword to confirm the cleaning operation."""
    return "YeS"

  @staticmethod
  def _get_paths_to_delete() -> List[str]:
    """
    ### Returns a list of all the paths to be deleted.

    #### Returns:
    - (list(str)): List containing all the paths to delete.
    """
    return [
      *[paths.get_source_path(source) for source in constants.XMIPP_SOURCES],
      paths.INSTALL_PATH,
      paths.BUILD_PATH,
      paths.CONFIG_FILE
    ]

  def _get_confirmation_message(self) -> str:
    """
    ### Returns message to be printed when asking for user confirmation.

    #### Returns:
    - (str): Confirmation message.
    """
    return '\n'.join([
      logger.yellow("WARNING: This will DELETE ALL content from src and build, and also the xmipp.conf file."),
      logger.yellow("\tNotice that if you have unpushed changes, they will be deleted."),
      logger.yellow(f"\nIf you are sure you want to do this, type '{self.confirmation_keyword}' (case sensitive):")
    ])
