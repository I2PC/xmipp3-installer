"""
### Mode Test Executor Module.

This module contains the class to execute Xmipp tests.
"""
import os
from typing import Dict, Tuple, Any

from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.application.logger.logger import logger, errors
from xmipp3_installer.installer import urls
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.installer.handlers import shell_handler
from xmipp3_installer.installer.modes.mode_sync.mode_sync_executor import ModeSyncExecutor
from xmipp3_installer.repository.config_vars import variables

_DATASET_NAME = "xmipp_programs"
_PYTHON_TEST_SCRIPT_PATH = os.path.join(paths.SOURCES_PATH, "xmipp")
_PYTHON_TEST_SCRIPT_INTERNAL_FOLDER = "tests"
_PYTHON_TEST_SCRIPT_NAME = "test.py"
_PYTHON_DATA_FOLDER = 'data'
_PYTHON_TEST_SCRIPT_INTERNAL_PATH = os.path.join(
  _PYTHON_TEST_SCRIPT_INTERNAL_FOLDER,
  _PYTHON_TEST_SCRIPT_NAME
)
_DEFAULT_PYTHON_HOME = "python3"
_DATASET_PATH = os.path.join(_PYTHON_TEST_SCRIPT_PATH, _PYTHON_TEST_SCRIPT_INTERNAL_FOLDER,  _PYTHON_DATA_FOLDER)
_TEST_DATA = os.path.join(_PYTHON_TEST_SCRIPT_INTERNAL_FOLDER, _PYTHON_DATA_FOLDER)
_BASHRC_FILE_PATH = os.path.abspath(os.path.join(paths.INSTALL_PATH, "xmipp.bashrc"))
_TESTS_SEPARATOR = " "
_PARAM_MAPPER = {
  params.PARAM_SHOW_TESTS: "--show",
  params.PARAM_ALL_FUNCTIONS: "--allFuncs",
  params.PARAM_ALL_PROGRAMS: "--allPrograms"
}

class ModeTestExecutor(ModeSyncExecutor):
  """Class to execute Xmipp tests."""

  def __init__(self, context: Dict):
    """
    ### Constructor.
    
    #### Params:
    - context (dict): Dictionary containing the installation context variables.
    """
    super().__init__(context)
    self.param_value = self.__get_selected_param_value(context)
    self.cuda = context.pop(variables.CUDA)
    python_home = context.pop(variables.PYTHON_HOME, None)
    self.python_home = python_home if python_home else _DEFAULT_PYTHON_HOME
  
  def run(self) -> Tuple[int, str]:
    """
    ### Runs the provided tests.

    #### Returns:
    - (tuple(int, str)): Tuple containing the return code and an error message if there was an error.
    """
    ret_code, output = self.__load_bashrc()
    if ret_code:
      return ret_code, output
    
    ret_code, output = super().run()
    if ret_code:
      return ret_code, output
    return self.__run_tests()

  def _sync_operation(self) -> Tuple[int, str]:
    """
    ### Executes the test operation.

    #### Returns:
    - (tuple(int, str)): Tuple containing the return code and an error message if there was an error.
    """
    if os.path.isdir(_DATASET_PATH):
      task_message = "Updating"
      task = "update"
    else:
      task_message = "Downloading"
      task = "download"
    logger(logger.blue(f"{task_message} the test files"))

    args = f"{_TEST_DATA} {urls.SCIPION_TESTS_URL} {_DATASET_NAME}"
    ret_code = shell_handler.run_shell_command_in_streaming(
      f"{self.sync_program_name} {task} {args}",
      cwd=_PYTHON_TEST_SCRIPT_PATH,
      show_output=True,
      show_error=True,
      substitute=True
    )
    ret_code = 1 if ret_code else ret_code
    return ret_code, ""

  @staticmethod
  def __load_bashrc() -> Tuple[int, str]:
    """
    ### Loads the bashrc file.

    #### Returns:
    - (tuple(int, str)): Tuple containing the return code and an error message if there was an error.
    """
    if not os.path.exists(_BASHRC_FILE_PATH):
      return errors.IO_ERROR, f"File {_BASHRC_FILE_PATH} does not exist."

    ret_code, output = shell_handler.run_shell_command(
      f"bash -c 'source {_BASHRC_FILE_PATH} && env'"
    )
    if ret_code:
      return 1, output

    for line in output.splitlines():
      key, _, value = line.partition("=")
      os.environ[key] = value
    return 0, ""

  def __run_tests(self) -> Tuple[int, str]:
    """
    ### Runs the specified tests.

    #### Returns:
    - (tuple(int, str)): Tuple containing the return code and an error message if there was an error.
    """
    no_cuda_str = "--noCuda" if not self.cuda else ""
    if self.param_value not in {
      _PARAM_MAPPER[params.PARAM_SHOW_TESTS],
      _PARAM_MAPPER[params.PARAM_ALL_FUNCTIONS],
      _PARAM_MAPPER[params.PARAM_ALL_PROGRAMS]
    }:
      test_names = self.param_value.replace(_TESTS_SEPARATOR, ", ")
      logger(f" Tests to run: {test_names}")
    ret_code, output = shell_handler.run_shell_command(
      f"{self.python_home} {_PYTHON_TEST_SCRIPT_INTERNAL_PATH} {self.param_value} {no_cuda_str}",
      cwd=_PYTHON_TEST_SCRIPT_PATH,
      show_output=True
    )
    ret_code = 1 if ret_code else 0
    return ret_code, output

  @staticmethod
  def __get_selected_param_value(context: Dict[str, Any]) -> str:
    """
    ### Returns the value of the param selected to run the test execution.

    #### Params:
    - context (dict(str, any)): Dictionary containing the installation context variables.

    #### Returns:
    - (str): The value of the selected variable to use
    """
    for variable in {
      params.PARAM_SHOW_TESTS,
      params.PARAM_ALL_FUNCTIONS,
      params.PARAM_ALL_PROGRAMS
    }:
      if context[variable]:
        return _PARAM_MAPPER[variable]
    return _TESTS_SEPARATOR.join(context.pop(params.PARAM_TEST_NAMES))
