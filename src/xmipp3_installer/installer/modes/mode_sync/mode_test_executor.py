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

	def __init__(self, context: Dict):
		"""
		### Constructor.
		
		#### Params:
		- context (dict): Dictionary containing the installation context variables.
		"""
		super().__init__(context)
		self.test_names = context.pop(params.PARAM_TEST_NAME)
		self.cuda = context.pop(variables.CUDA)
		self.xmipp_src = os.environ.get('XMIPP_SRC', None)
		self.tests_path = None
		self.dataset_path = None
		if self.xmipp_src and os.path.isdir(self.xmipp_src):
			os.environ['PYTHONPATH'] = ':'.join([
				os.path.join(self.xmipp_src, constants.XMIPP),
				os.environ.get('PYTHONPATH', '')
			])
			self.tests_path = os.path.join(self.xmipp_src, constants.XMIPP, 'tests')
			self.dataset_path = os.path.join(self.tests_path, 'data')

	def _sync_operation(self) -> Tuple[int, str]:
		"""
		### Executes the test operation.

		#### Returns:
		- (tuple(int, str)): Tuple containing the return code and an error message if there was an error.
		"""
		if not self.xmipp_src or not os.path.isdir(self.xmipp_src):
			logger(logger.red("XMIPP_SRC environment variable not set or directory does not exist"))
			return 1, "Environment error"

		dataset = 'xmipp_programs'
		if os.path.isdir(self.dataset_path):
			logger(logger.blue("Updating the test files"))
			task = "update"
			show_output = False
		else:
			logger(logger.blue("Downloading the test files"))
			task = "download"
			show_output = True

		args = f"tests/data {urls.SCIPION_TESTS_URLS} {dataset}"
		ret_code, output = shell_handler.run_shell_command(
			f"{self.sync_program_path} {task} {args}",
			cwd=os.path.join(constants.SOURCES_PATH, constants.XMIPP),
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
		no_cuda_str = '--noCuda' if self.cuda == 'OFF' else ''
		logger(f" Tests to do: {', '.join(self.test_names)}")

		# TODO: Should be scipion3?
		python_exe = 'python3'
		test_scripts = os.path.dirname(os.environ['XMIPP_TEST_DATA'])

		return shell_handler.run_shell_command(
			f"{python_exe} test.py {' '.join(self.test_names)} {no_cuda_str}",
			cwd=test_scripts,
			show_output=True,
			show_error=True
		)
