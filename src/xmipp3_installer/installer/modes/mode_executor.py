from abc import ABC, abstractmethod
from typing import Dict

from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer import constants

class ModeExecutor(ABC):
  """
  ### Base executor interface for installer modes.
  """
  def __init__(self, args: Dict):
    super().__init__()
    self.args = args
    self._set_logger_config()
    self.__configure_logging()
  
  def _set_logger_config(self):
    """
    ### Sets the specific logger params for this mode.
    """
    self.logs_to_file = False
    self.prints_with_substitution = False
  
  def __configure_logging(self):
    """
    ### Configures the logger according to the specified config.
    """
    if self.logs_to_file:
      logger.start_log_file(constants.LOG_FILE)
    if self.prints_with_substitution:
      logger.set_allow_substitution(True)
  
  @abstractmethod
  def run(self) -> int: ...
