import os
from abc import abstractmethod
from typing import Dict, Tuple

from xmipp3_installer.application.logger import errors
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer import constants
from xmipp3_installer.installer.modes import mode_executor

_SYNC_PROGRAM_PATH = os.path.join(".", constants.BINARIES_PATH)
_SYNC_PROGRAM_NAME = "xmipp_sync_data"

class ModeModelsExecutor(mode_executor.ModeExecutor):
	"""Base class for model-related mode executors."""

	def __init__(self, context: Dict):
		"""
		### Constructor.
		
		#### Params:
		- context (dict): Dictionary containing the installation context variables.
		"""
		super().__init__(context)
		self.sync_program_path = os.path.join(_SYNC_PROGRAM_PATH, _SYNC_PROGRAM_NAME)

	def run(self) -> Tuple[int, str]:
		"""
		### Executes the model operation.

		#### Returns:
		- (tuple(int, str)): Tuple containing the return code and an error message if there was an error.
		"""
		if not os.path.exists(self.sync_program_path):
			logger('\n'.join([
				logger.red(f"{self.sync_program_path} does not exist."),
				logger.red("Xmipp needs to be compiled successfully before running this command!")
			]))
			return errors.IO_ERROR, ""
		return self._execute_model_operation()

	@abstractmethod
	def _execute_model_operation(self) -> Tuple[int, str]:
		"""
		### Executes the specific model operation.

		#### Returns:
		- (tuple(int, str)): Tuple containing the return code and an error message if there was an error.
		"""
