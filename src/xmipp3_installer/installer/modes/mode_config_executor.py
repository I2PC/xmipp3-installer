from typing import Dict, Tuple

from xmipp3_installer.application.logger import errors
from xmipp3_installer.application.logger import predefined_messages
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.installer.modes import mode_executor
from xmipp3_installer.repository import config

class ModeConfigExecutor(mode_executor.ModeExecutor):
	def __init__(self, args: Dict):
		super().__init__(args)
		self.overwrite = args.get(params.PARAM_OVERWRITE, False)
		self.config_values = {}
	
	def run(self) -> Tuple[int, str]:
		"""
		### Reads the config file and writes to it formatting properly with the appropiate values.

		#### Returns:
		- (tuple(int, str)): Tuple containing the error status and an error message if there was an error. 
		"""
		logger(predefined_messages.get_section_message("Managing config file"))
		logger(predefined_messages.get_working_message())
		try:
			file_handler = config.ConfigurationFileHandler()
			file_handler.write_config(overwrite=self.overwrite)
		except PermissionError as permission_error:
			return errors.IO_ERROR, str(permission_error)
		self.config_values = file_handler.values
		logger(predefined_messages.get_done_message(), substitute=True)
		return 0, ""
	