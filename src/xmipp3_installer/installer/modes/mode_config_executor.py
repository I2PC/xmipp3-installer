from typing import Dict

from xmipp3_installer.installer.modes import mode_executor
from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.repository import config

class ModeConfigExecutor(mode_executor.ModeExecutor):
	def __init__(self, args: Dict):
		super().__init__(args)
		self.overwrite = args.get(params.PARAM_OVERWRITE, False)
	
	def run(self) -> int:
		try:
			file_handler = config.ConfigurationFileHandler()
			file_handler.write_config(overwrite=self.overwrite)
		except PermissionError:
			return 1
		self.config_values = file_handler.values
		return 0
	