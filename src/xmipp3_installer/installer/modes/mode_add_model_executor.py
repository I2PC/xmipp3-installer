import os
from typing import Dict, Tuple

from xmipp3_installer.application.logger import errors
from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer.modes import mode_executor

class ModeVersionExecutor(mode_executor.ModeExecutor):
	def __init__(self, args: Dict):
		"""
		### Constructor.
		
		#### Params:
		- args (dict): Dictionary containing all parsed command-line arguments.
		"""
		super().__init__(args)
		self.login = args.pop(params.PARAM_LOGIN)
		self.model_path = args.pop(params.PARAM_MODEL_PATH)
		self.update = args.pop(params.PARAM_UPDATE, False)

	def run(self) -> Tuple[int, str]:
		"""
		### Collects all the version information available and displays it.

		#### Returns:
		- (tuple(int, str)): Tuple containing the error status and an error message if there was an error.
		"""
		if not os.path.isdir(self.model_path):
			logger('\n'.join([
				logger.red(f"{self.model_path} is not a directory. Please, check the path."),
				logger.red("The name of the model will be the name of that folder.")
			]))
			return errors.IO_ERROR, f"{self.model_path} is not a directory"
		return 0, ""
