import os
from typing import Dict, Tuple

from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer import constants
from xmipp3_installer.installer.modes import mode_executor
from xmipp3_installer.installer.handlers import shell_handler

class ModeGitExecutor(mode_executor.ModeExecutor):
	def __init__(self, context: Dict):
		"""
		### Constructor.
		
		#### Params:
		- context (dict): Dictionary containing the installation context variables.
		"""
		super().__init__(context)
		command_param_list = context.pop(params.PARAM_GIT_COMMAND)
		self.command = ' '.join(command_param_list)
	
	def run(self) -> Tuple[int, str]:
		"""
		### Executes the given git command into all xmipp source repositories.

		#### Returns:
		- (tuple(int, str)): Tuple containing the return code and an error message if there was an error.
		"""
		cmd = f"git {self.command}"
		logger(f"Running command '{cmd}' for all xmipp sources...")

		for source in [constants.XMIPP, constants.XMIPP_CORE]:
			logger("")
			ret_code, output = self.__execute_git_command_for_source(source, cmd)
			if ret_code:
				return ret_code, output

		return 0, ""

	def __execute_git_command_for_source(self, source: str, cmd: str) -> Tuple[int, str]:
		"""
		### Executes the git command for a specific source.

		#### Params:
		- source (str): The source repository name.
		- cmd (str): The git command to execute.

		#### Returns:
		- (tuple(int, str)): Tuple containing the return code and output message.
		"""
		source_path = os.path.abspath(os.path.join(constants.SOURCES_PATH, source))
		if not os.path.exists(source_path):
			logger(logger.yellow(
				f"WARNING: Source {source} does not exist in path {source_path}. Skipping."
			))
			return 0, ""

		logger(logger.blue(
			f"Running command for {source} in path {source_path}..."
		))
		
		return shell_handler.run_shell_command(
			cmd,
			cwd=source_path,
			show_output=True,
			show_error=True
		) 