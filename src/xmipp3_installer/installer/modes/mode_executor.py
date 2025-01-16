from abc import ABC, abstractmethod
from typing import Dict, Tuple

from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer import constants

class ModeExecutor(ABC):
  """
  ### Base executor interface for installer modes.
  """
  def __init__(self, args: Dict):
    """
		### Constructor.
		
		#### Params:
		- args (dict): Dictionary containing all parsed command-line arguments.
		"""
    super().__init__()
    self.args = args
    self._set_executor_config()
    self.__configure_logger()
  
  def _set_executor_config(self):
    """
    ### Sets the specific executor params for this mode.
    """
    self.logs_to_file = False
    self.prints_with_substitution = False
    self.prints_banner_on_exit = False
    self.sends_installation_info = False
  
  def __configure_logger(self):
    """
    ### Configures the logger according to the specified config.
    """
    if self.logs_to_file:
      logger.start_log_file(constants.LOG_FILE)
    if self.prints_with_substitution:
      logger.set_allow_substitution(True)
  
  @abstractmethod
  def run(self) -> Tuple[int, str]:
    """Run method to be implemented by inheriting classes."""
