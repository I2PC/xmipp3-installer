import os
from typing import Tuple, List

from xmipp3_installer.application import user_interactions
from xmipp3_installer.application.logger import errors
from xmipp3_installer.application.logger import predefined_messages
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer import constants
from xmipp3_installer.installer.modes import mode_executor
from xmipp3_installer.repository import file_operations

class ModeCleanAllExecutor(mode_executor.ModeExecutor):
	def run(self) -> Tuple[int, str]:
		"""
		### Deletes the compiled binaries.

		#### Returns:
		- (tuple(int, str)): Tuple containing the error status and an error message if there was an error. 
		"""
		if not ModeCleanAllExecutor.__get_confirmation():
			return errors.INTERRUPTED_ERROR, ""
		file_operations.delete_paths(ModeCleanAllExecutor.__get_paths_to_delete())
		logger(predefined_messages.get_done_message())
		return 0, ""
	
	@staticmethod
	def __get_confirmation() -> bool:
		"""
		### Asks the user for confirmation.

		#### Returns:
		- (bool): True if the user confirms, False otherwise.
		"""
		confirmation_text = "YeS"
		logger('\n'.join([
			logger.yellow("WARNING: This will DELETE ALL content from src and build, and also the xmipp.conf file."),
			logger.yellow("\tNotice that if you have unpushed changes, they will be deleted."),
			logger.yellow(f"\nIf you are sure you want to do this, type '{confirmation_text}' (case sensitive):")
		]))
		return user_interactions.get_user_confirmation(confirmation_text)
	
	@staticmethod
	def __get_paths_to_delete() -> List[str]:
		"""
		### Returns a list of all the paths to be deleted.

		#### Returns:
		- (list(str)): List containing all the paths to delete.
		"""
		return [
			*[
				os.path.join(constants.SOURCES_PATH, source)
				for source in constants.XMIPP_SOURCES
			],
			constants.INSTALL_PATH,
			constants.BUILD_PATH,
			constants.CONFIG_FILE
		]

