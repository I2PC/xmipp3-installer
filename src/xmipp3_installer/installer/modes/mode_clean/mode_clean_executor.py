"""
### Mode Clean Executor Module.

This module contains the base class for executors that clean compiled binaries.
"""

from abc import abstractmethod
from typing import Tuple, List

from xmipp3_installer.application import user_interactions
from xmipp3_installer.application.logger import errors
from xmipp3_installer.application.logger import predefined_messages
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer.modes import mode_executor
from xmipp3_installer.shared import file_operations

class ModeCleanExecutor(mode_executor.ModeExecutor):
  """
  ### Mode Clean Executor.

  Base class for executors that clean compiled binaries.
  """
  
  def run(self) -> Tuple[int, str]:
    """
    ### Deletes the compiled binaries.

    #### Returns:
    - (tuple(int, str)): Tuple containing the error status and an error message if there was an error. 
    """
    if not self.__get_confirmation():
      return errors.INTERRUPTED_ERROR, ""
    file_operations.delete_paths(self.__class__._get_paths_to_delete())
    logger(predefined_messages.get_done_message())
    return 0, ""
  
  def __get_confirmation(self) -> bool:
    """
    ### Asks the user for confirmation.

    #### Returns:
    - (bool): True if the user confirms, False otherwise.
    """
    logger(self._get_confirmation_message())
    return user_interactions.get_user_confirmation(self.confirmation_keyword)
  
  @property
  @abstractmethod
  def confirmation_keyword(self) -> str:
    """### Confirmation keyword propery to be defined by inheriting classes."""

  @staticmethod
  @abstractmethod
  def _get_paths_to_delete() -> List[str]:
    """Get paths to delete method to be implemented by the inheriting classes."""
  
  @abstractmethod
  def _get_confirmation_message(self) -> str:
    """Get confirmation message method to be implemented by the inheriting classes."""
