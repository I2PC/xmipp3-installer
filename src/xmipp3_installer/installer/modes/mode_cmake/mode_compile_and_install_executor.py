from typing import Tuple, Dict

from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.application.logger import predefined_messages, errors
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer import constants, urls
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.installer.handlers import shell_handler, git_handler
from xmipp3_installer.installer.modes.mode_cmake import mode_cmake_executor

class ModeCompileAndInstallExecutor(mode_cmake_executor.ModeCMakeExecutor):
	def __init__(self, context: Dict):
		"""
		### Constructor.
		
		#### Params:
		- context (dict): Dictionary containing the installation context variables.
		"""
		super().__init__(context)
		self.target_branch = context[params.PARAM_BRANCH]
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
		cmd = f"{cmake} --build {paths.BUILD_PATH} --config {self.build_type} -j {self.jobs}"
		if shell_handler.run_shell_command_in_streaming(cmd, show_output=True, substitute=self.substitute):
			return errors.CMAKE_COMPILE_ERROR, ""
		
		installation_section_message = predefined_messages.get_section_message("Installing with CMake")
		logger(f"\n{installation_section_message}")
		cmd = f"{cmake} --install {paths.BUILD_PATH} --config {self.build_type}"
		if shell_handler.run_shell_command_in_streaming(cmd, show_output=True, substitute=self.substitute):
			return errors.CMAKE_INSTALL_ERROR, ""
		return 0, ""
	
	def __switch_branches(self) -> Tuple[int, str]:
		"""
		### Switches all sources to the target branch if specified.

		#### Returns:
		- (tuple(int, str)): Tuple containing the error status and an error message if there was an error.
		"""
		if not self.target_branch:
			return 0, ""
		
		for source in constants.XMIPP_SOURCES:
			repo_url = f"{urls.I2PC_REPOSITORY_URL}{source}.git"
			if not git_handler.branch_exists_in_repo(repo_url, self.target_branch):
				logger(logger.yellow(
					f"WARNING: Branch {self.target_branch} does not exist in source {source}. Skipping."
				))
				continue
			ret_code, output = git_handler.execute_git_command_for_source(
				f"checkout {self.target_branch}", source
			)
			if ret_code:
				return ret_code, output
		return 0, ""
