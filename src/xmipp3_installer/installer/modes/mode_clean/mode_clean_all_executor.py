import os
from typing import List

from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer import constants
from xmipp3_installer.installer.modes.mode_clean import mode_clean_executor

class ModeCleanAllExecutor(mode_clean_executor.ModeCleanExecutor):
	def _get_paths_to_delete(self) -> List[str]:
		"""
		### Returns a list of all the paths to be deleted.

		#### Returns:
		- (list(str)): List containing all the paths to delete.
		"""
		return [
			constants.XMIPP_CORE_PATH,
			constants.INSTALL_PATH,
			constants.BUILD_PATH,
			constants.CONFIG_FILE
		]
	
	def _get_confirmation_keyword(self) -> str:
		"""
		### Returns the keyword needed to be introduced by the user to confirm an operation.

		#### Returns:
		- (str): Confirmation keyword.
		"""
		return "YeS"

	def _get_confirmation_message(self) -> str:
		"""
		### Returns message to be printed when asking for user confirmation.

		#### Returns:
		- (str): Confirmation message.
		"""
		return '\n'.join([
			logger.yellow("WARNING: This will DELETE ALL content from src and build, and also the xmipp.conf file."),
			logger.yellow("\tNotice that if you have unpushed changes, they will be deleted."),
			logger.yellow(f"\nIf you are sure you want to do this, type '{self._get_confirmation_keyword()}' (case sensitive):")
		])
	