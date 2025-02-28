import shutil
from abc import abstractmethod
from typing import Dict, Tuple, Optional

from xmipp3_installer.application.logger import errors
from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.installer.modes import mode_executor
from xmipp3_installer.repository.config_vars import variables

class ModeCMakeExecutor(mode_executor.ModeExecutor):
	def __init__(self, context: Dict):
		"""
		### Constructor.
		
		#### Params:
		- context (dict): Dictionary containing the installation context variables.
		"""
		super().__init__(context)
		self.substitute = not context[params.PARAM_KEEP_OUTPUT]

	def run(self) -> Tuple[int, str]:
		"""
		### Runs the CMake config with the appropiate params.

		#### Returns:
		- (tuple(int, str)): Tuple containing the error status and an error message if there was an error. 
		"""
		cmake = self.__get_cmake_executable()
		if not cmake:
			return errors.CMAKE_ERROR, "CMake installation not found."
		return self._run_cmake_mode(cmake)
	
	def _set_executor_config(self):
		"""
		### Sets the specific executor params for this mode.
		"""
		super()._set_executor_config()
		self.logs_to_file = True
		self.prints_with_substitution = True
		self.sends_installation_info = True
	
	def __get_cmake_executable(self) -> Optional[str]:
		"""
		### Returns the path to the CMake executable to be used.

		#### Returns:
		- (str | None): Path to the CMake executable. None if it was not found.
		"""
		cmake = self.context[variables.CMAKE]
		return cmake if cmake else shutil.which("cmake")
	
	@abstractmethod
	def _run_cmake_mode(self, cmake: str) -> Tuple[int, str]:
		"""Run CMake mode method to be implemented by inheriting classes."""
	