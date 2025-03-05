from typing import Tuple, Dict

from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.application.logger import predefined_messages, errors
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer import constants
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.installer.handlers import shell_handler
from xmipp3_installer.installer.modes import mode_git_executor
from xmipp3_installer.installer.modes.mode_cmake import mode_cmake_executor

class ModeCompileAndInstallExecutor(mode_cmake_executor.ModeCMakeExecutor):
	def __init__(self, context: Dict):
		"""
		### Constructor.
		
		#### Params:
		- context (dict): Dictionary containing the installation context variables.
		"""
		self.target_branch = context[params.PARAM_BRANCH]
		self.git_executor = mode_git_executor.ModeGitExecutor(
			{**context, params.PARAM_GIT_COMMAND: ["checkout", self.target_branch]}
		) if self.target_branch else None
		super().__init__(context)
		self.jobs = context[params.PARAM_JOBS]

	def _set_executor_config(self):
		"""
		### Sets the specific executor params for this mode.
		"""
		super()._set_executor_config()
		self.prints_banner_on_exit = True

	def _run_cmake_mode(self, cmake: str) -> Tuple[int, str]:
		"""
		### Runs the CMake compilation & installation with the appropiate params.

		#### Params:
		- cmake (str): Path to CMake executable.

		#### Returns:
		- (tuple(int, str)): Tuple containing the error status and an error message if there was an error. 
		"""
		ret_code, output = self.__switch_branches()
		if ret_code:
			return ret_code, output

		logger(predefined_messages.get_section_message("Compiling with CMake"))
		cmd = f"{cmake} --build {paths.BUILD_PATH} --config {constants.BUILD_TYPE} -j {self.jobs}"
		if shell_handler.run_shell_command_in_streaming(cmd, show_output=True, substitute=self.substitute):
			return errors.CMAKE_COMPILE_ERROR, ""
		
		installation_section_message = predefined_messages.get_section_message("Installing with CMake")
		logger(f"\n{installation_section_message}")
		cmd = f"{cmake} --install {paths.BUILD_PATH} --config {constants.BUILD_TYPE}"
		if shell_handler.run_shell_command_in_streaming(cmd, show_output=True, substitute=self.substitute):
			return errors.CMAKE_INSTALL_ERROR, ""
		return 0, ""
	
	def __switch_branches(self) -> Tuple[int, str]:
		"""
		### Switches all sources to the target branch if specified.

		#### Returns:
		- (tuple(int, str)): Tuple containing the error status and an error message if there was an error.
		"""
		ret_code, output = self.git_executor.run() if self.target_branch else (0, "")
		return ret_code, output
