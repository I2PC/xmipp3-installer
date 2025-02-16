import os
from typing import Dict, Tuple

from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer import constants, urls
from xmipp3_installer.installer.handlers import shell_handler
from xmipp3_installer.installer.modes.mode_sync.mode_sync_executor import ModeSyncExecutor
from xmipp3_installer.repository.config_vars import variables

class ModeTestExecutor(ModeSyncExecutor):
	"""Class to execute Xmipp tests."""
	DATASET_NAME = "xmipp_programs"
	PYTHON_TEST_SCRIPT_PATH = os.path.join(constants.BINARIES_PATH, "tests")
	PYTHON_TEST_SCRIPT_NAME = "test.py"
	DATASET_PATH = os.path.join(PYTHON_TEST_SCRIPT_PATH, 'data')

	def __init__(self, context: Dict):
		"""
		### Constructor.
		
		#### Params:
		- context (dict): Dictionary containing the installation context variables.
		"""
		super().__init__(context)
		self.test_names = context.pop(params.PARAM_TEST_NAMES)
		self.cuda = context.pop(variables.CUDA)
		self.show = context.pop(params.PARAM_SHOW_TESTS)
		python_home = context.pop(variables.PYTHON_HOME, None)
		self.python_home = python_home if python_home else "python3"

	def _sync_operation(self) -> Tuple[int, str]:
		"""
		### Executes the test operation.

		#### Returns:
		- (tuple(int, str)): Tuple containing the return code and an error message if there was an error.
		"""
		if os.path.isdir(self.DATASET_PATH):
			task_message = "Updating"
			task = "update"
			show_output = False
		else:
			task_message = "Downloading"
			task = "download"
			show_output = True
		logger(logger.blue(f"{task_message} the test files"))

		args = f"{self.DATASET_PATH} {urls.SCIPION_TESTS_URL} {self.DATASET_NAME}"
		sync_program_relative_call = os.path.join(
			".",
			os.path.basename(self.sync_program_path)
		)
		ret_code, output = shell_handler.run_shell_command(
			f"{sync_program_relative_call} {task} {args}",
			cwd=os.path.dirname(self.sync_program_path),
			show_output=show_output
		)

		if ret_code:
			return ret_code, output
		return self.__run_tests()

	def __run_tests(self) -> Tuple[int, str]:
		"""
		### Runs the specified tests.

		#### Returns:
		- (tuple(int, str)): Tuple containing the return code and an error message if there was an error.
		"""
		no_cuda_str = "--noCuda" if not self.cuda else ""
		show_str = "--show" if self.show else ""
		logger(f" Tests to run: {', '.join(self.test_names)}")
		
		return shell_handler.run_shell_command(
			f"{self.python_home} {self.PYTHON_TEST_SCRIPT_NAME} {' '.join(self.test_names)} {no_cuda_str}{show_str}",
			cwd=self.PYTHON_TEST_SCRIPT_PATH,
			show_output=True,
			show_error=True
		)
