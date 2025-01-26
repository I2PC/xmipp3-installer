import glob
import os
import pathlib
from typing import Tuple, List

from xmipp3_installer.application import user_interactions
from xmipp3_installer.application.logger import errors
from xmipp3_installer.application.logger import predefined_messages
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer import constants
from xmipp3_installer.installer.modes import mode_executor
from xmipp3_installer.installer.tmp import versions
from xmipp3_installer.repository import file_operations

class ModeCleanBinExecutor(mode_executor.ModeExecutor):
	def run(self) -> Tuple[int, str]:
		"""
		### Deletes the compiled binaries.

		#### Returns:
		- (tuple(int, str)): Tuple containing the error status and an error message if there was an error. 
		"""
		if not ModeCleanBinExecutor.__get_confirmation():
			return errors.INTERRUPTED_ERROR, ""
		file_operations.delete_paths([
			*ModeCleanBinExecutor.__get_paths_to_delete(),
			constants.BUILD_PATH
		])
		logger(predefined_messages.get_done_message())
		return 0, ""
	
	@staticmethod
	def __get_confirmation() -> bool:
		"""
		### Asks the user for confirmation.

		#### Returns:
		- (bool): True if the user confirms, False otherwise.
		"""
		confirmation_text = "y"
		logger('\n'.join([
			logger.yellow(f"WARNING: This will DELETE from {constants.SOURCES_PATH} all *.so, *.os and *.o files. Also the *.pyc and *.dblite files"),
			logger.yellow(f"If you are sure you want to do this, type '{confirmation_text}' (case sensitive):")
		]))
		return user_interactions.get_user_confirmation(confirmation_text)

	@staticmethod
	def __get_paths_to_delete() -> List[str]:
		"""
		### Returns a list of all the paths to be deleted.

		#### Returns:
		- (list(str)): List containing all the paths to delete.
		"""
		dblite_files = glob.glob(
			"**/.dblite",
			recursive=True
		)
		return [
			*dblite_files,
			*ModeCleanBinExecutor.__get_compilation_files(),
			*ModeCleanBinExecutor.__get_empty_dirs(),
			*ModeCleanBinExecutor.__get_pycache_dirs(),
			constants.BUILD_PATH
		]
	
	@staticmethod
	def __get_compilation_files():
		"""
		### Returns a list of all the compilation-related files.

		#### Returns:
		- (list(str)): List containing all the paths to compilation-related files.
		"""
		compilation_files = []
		for pattern in ['**/*.so', '**/*.os', '**/*.o']:
			compilation_files.extend(
				glob.glob(pattern, recursive=True, root_dir=constants.SOURCES_PATH)
			)
		return compilation_files

	@staticmethod
	def __get_empty_dirs() -> List[str]:
		"""
		### Returns a list with all the empty directories inside the programs folder.

		#### Returns:
		- (list(str)): List containing the paths to all the empty directories.
		"""
		empty_dirs = [] 
		for root, dirs, files in os.walk(os.path.join(
			constants.SOURCES_PATH, versions.XMIPP, "applications", "programs"
		)): 
			if not len(dirs) and not len(files): 
				empty_dirs.append(root) 
		return empty_dirs

	@staticmethod
	def __get_pycache_dirs() -> List[str]:
		"""
		### Returns a list of all the __pycache__ directories.

		#### Returns:
		- (list(str)): List containing all the paths to __pycache__ directories.
		"""
		return [
			str(path) for path in pathlib.Path().rglob('__pycache__')
		]
	