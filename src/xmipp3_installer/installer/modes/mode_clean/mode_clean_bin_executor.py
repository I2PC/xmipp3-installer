import glob
import os
import pathlib
from typing import List

from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer import constants
from xmipp3_installer.installer.modes.mode_clean import mode_clean_executor

class ModeCleanBinExecutor(mode_clean_executor.ModeCleanExecutor):
	def _get_paths_to_delete(self) -> List[str]:
		"""
		### Returns a list of all the paths to be deleted.

		#### Returns:
		- (list(str)): List containing all the paths to delete.
		"""
		dblite_files = glob.glob(
			"**/*.dblite",
			recursive=True
		)
		return [
			*dblite_files,
			*ModeCleanBinExecutor.__get_compilation_files(),
			*ModeCleanBinExecutor.__get_empty_dirs(),
			*ModeCleanBinExecutor.__get_pycache_dirs(),
			constants.BUILD_PATH
		]

	def _get_confirmation_keyword(self) -> str:
		"""
		### Returns the keyword needed to be introduced by the user to confirm an operation.

		#### Returns:
		- (str): Confirmation keyword.
		"""
		return "y"
	
	def _get_confirmation_message(self) -> str:
		"""
		### Returns message to be printed when asking for user confirmation.

		#### Returns:
		- (str): Confirmation message.
		"""
		return '\n'.join([
			logger.yellow(f"WARNING: This will DELETE from {constants.SOURCES_PATH} all *.so, *.os and *.o files. Also the *.pyc and *.dblite files"),
			logger.yellow(f"If you are sure you want to do this, type '{self._get_confirmation_keyword()}' (case sensitive):")
		])
	
	@staticmethod
	def __get_compilation_files():
		"""
		### Returns a list of all the compilation-related files.

		#### Returns:
		- (list(str)): List containing all the paths to compilation-related files.
		"""
		compilation_files = []
		for root, _, files in os.walk(constants.SOURCES_PATH):
			for pattern in ['*.so', '*.os', '*.o']:
				for filename in glob.fnmatch.filter(files, pattern):
					compilation_files.append(os.path.join(root, filename))
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
			constants.SOURCES_PATH, constants.XMIPP, "applications", "programs"
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
	