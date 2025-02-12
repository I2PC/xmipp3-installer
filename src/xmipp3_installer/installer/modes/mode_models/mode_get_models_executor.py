import os
from typing import Dict, Tuple

from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer import constants, urls
from xmipp3_installer.installer.handlers import shell_handler
from xmipp3_installer.installer.modes.mode_models.mode_models_executor import ModeModelsExecutor

class ModeGetModelsExecutor(ModeModelsExecutor):
	def __init__(self, context: Dict):
		"""
		### Constructor.
		
		#### Params:
		- context (dict): Dictionary containing the installation context variables.
		"""
		super().__init__(context)
		self.models_directory = context.pop(params.PARAM_MODELS_DIRECTORY)
		self.dist_path = os.path.join(constants.SOURCES_PATH, constants.XMIPP)
		if self.models_directory == self.dist_path:
			self.models_directory = os.path.join(self.models_directory, 'models')

	def _execute_model_operation(self) -> Tuple[int, str]:
		"""
		### Downloads deep learning models.

		#### Returns:
		- (tuple(int, str)): Tuple containing the return code and an error message if there was an error.
		"""
		if os.path.isdir(self.models_directory):
			task = "update"
			in_progress_task = "Updating"
			completed_task = "updated"
		else:
			task = "download"
			in_progress_task = "Downloading"
			completed_task = "downloaded"
		
		logger(f"{in_progress_task} Deep Learning models (in background)")
		ret_code, output = shell_handler.run_shell_command(
			f"{self.sync_program_path} {task} {self.models_directory} {urls.MODELS_URL} DLmodels",
			show_command=True,
			show_output=True,
			show_error=True
		)
		if not ret_code:
			logger(logger.green(f"Models successfully {completed_task}!"))

		return ret_code, output
