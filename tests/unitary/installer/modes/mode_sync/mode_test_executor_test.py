import os
from unittest.mock import patch

import pytest

from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.application.logger import errors
from xmipp3_installer.installer import urls
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.installer.modes.mode_sync import mode_sync_executor
from xmipp3_installer.installer.modes.mode_sync import mode_test_executor
from xmipp3_installer.installer.modes.mode_sync.mode_test_executor import ModeTestExecutor
from xmipp3_installer.repository.config_vars import variables

from ..... import get_assertion_message

__BINARIES_PATH = "/path/to/binaries"
__SINGLE_TEST = "test1"
__MULTIPLE_TESTS = [__SINGLE_TEST, "test2", "test3"]
__CONTEXT = {
  "testNames": __MULTIPLE_TESTS,
  params.PARAM_SHOW_TESTS: False,
  variables.CUDA: True,
  params.PARAM_ALL_FUNCTIONS: False,
  params.PARAM_ALL_PROGRAMS: False
}
__PYHTON_HOME = "/path/to/python"
__DATASET_PATH = "/path/to/dataset"
__DATASET_NAME = "dataset_name"
__PYTHON_TEST_SCRIPT_PATH = "/path/to/python_script"
__PYTHON_TEST_SCRIPT_NAME = "script_name"
_BASHRC_FILE_PATH = "/path/to/bashrc_file"
__ENV_VARIABLES_STR = """VAR1=VALUE1
VAR2=VALUE2
VAR3=VALUE3"""
__ENV_VARIABLES = {
  "VAR1": "VALUE1",
  "VAR2": "VALUE2",
  "VAR3": "VALUE3"
}

def test_implements_interface_mode_sync_executor():
  executor = ModeTestExecutor(__CONTEXT.copy())
  assert (
    isinstance(executor, mode_sync_executor.ModeSyncExecutor)
  ), get_assertion_message(
    "parent class",
    mode_sync_executor.ModeSyncExecutor.__name__,
    executor.__class__.__bases__[0].__name__
  )

@pytest.mark.parametrize(
  "python_context,tests,show,all_funcs,"
  "all_programs,expected_python_home,expected_param",
  [
    pytest.param(None, [], True, False, False, "python3", "--show"),
    pytest.param("", [], True, False, False, "python3", "--show"),
    pytest.param("whatever", [], True, False, False, "whatever", "--show"),
    pytest.param(None, [], False, True, False, "python3", "--allFuncs"),
    pytest.param(None, [], False, False, True, "python3", "--allPrograms"),
    pytest.param(None, ["test1"], False, False, False, "python3", "test1"),
    pytest.param(None, ["test1", "test2"], False, False, False, "python3", "test1 test2")
  ]
)
def test_sets_expected_values_when_initializing(
  python_context,
  tests,
  show,
  all_funcs,
  all_programs,
  expected_python_home,
  expected_param
):
  executor = ModeTestExecutor({
    **__CONTEXT,
    params.PARAM_TEST_NAMES: tests,
    params.PARAM_SHOW_TESTS: show,
    params.PARAM_ALL_FUNCTIONS: all_funcs,
    params.PARAM_ALL_PROGRAMS: all_programs,
    variables.PYTHON_HOME: python_context
  })
  values = (
    executor.cuda,
    executor.python_home,
    executor.param_value
  )
  expected_values = (
    True,
    expected_python_home,
    expected_param
  )
  assert (
    values == expected_values
  ), get_assertion_message("stored values", expected_values, values)

@pytest.mark.parametrize(
  "python_context,expected_python_home",
  [
    pytest.param({}, "python3"),
    pytest.param({variables.PYTHON_HOME: None}, "python3"),
    pytest.param({variables.PYTHON_HOME: ""}, "python3"),
    pytest.param({variables.PYTHON_HOME: "whatever"}, "whatever")
  ]
)
def test_sets_expected_python_home_expected_value(
  python_context,
  expected_python_home
):
  executor = ModeTestExecutor({**__CONTEXT, **python_context})
  assert (
    executor.python_home == expected_python_home
  ), get_assertion_message(
    "python home value",
    expected_python_home,
    executor.python_home
  )

@pytest.mark.parametrize(
  "missing_key",
  [
    pytest.param(params.PARAM_TEST_NAMES),
    pytest.param(variables.CUDA),
    pytest.param(params.PARAM_SHOW_TESTS)
  ]
)
def test_raises_key_error_when_param_not_present(missing_key):
  context = __CONTEXT.copy()
  del context[missing_key]
  with pytest.raises(KeyError):
    ModeTestExecutor(context)

def test_calls_run_shell_command_if_file_exists_when_loading_bashrc(
  __mock_os_path_exists,
  __mock_run_shell_command,
  __mock_bashrc_file_path
):
  ModeTestExecutor(__CONTEXT.copy())._ModeTestExecutor__load_bashrc()
  __mock_run_shell_command.assert_called_once_with(
    f"bash -c 'source {__mock_bashrc_file_path} && env'"
  )

def test_does_not_call_run_shell_command_if_file_does_not_exist_when_loading_bashrc(
  __mock_os_path_exists,
  __mock_run_shell_command,
  __mock_bashrc_file_path
):
  __mock_os_path_exists.return_value = False
  ModeTestExecutor(__CONTEXT.copy())._ModeTestExecutor__load_bashrc()
  __mock_run_shell_command.assert_not_called()

def test_loads_env_variables_when_loading_bashrc(
  __mock_os_path_exists,
  __mock_run_shell_command
):
  __mock_run_shell_command.return_value = (0, __ENV_VARIABLES_STR)
  ModeTestExecutor(__CONTEXT.copy())._ModeTestExecutor__load_bashrc()
  for variable in __ENV_VARIABLES.keys():
    assert (
      variable in os.environ
    ), f"Variable {variable} not found in environment variables."
    assert (
      os.environ[variable] == __ENV_VARIABLES[variable]
    ), get_assertion_message("env variable value", __ENV_VARIABLES[variable], os.environ[variable])

@pytest.mark.parametrize(
  "__mock_os_path_exists,__mock_run_shell_command,expected_result",
  [
    pytest.param(False, (1, "error"), (errors.IO_ERROR, f"File {_BASHRC_FILE_PATH} does not exist.")),
    pytest.param(False, (0, ""), (errors.IO_ERROR, f"File {_BASHRC_FILE_PATH} does not exist.")),
    pytest.param(True, (1, "error"), (1, "error")),
    pytest.param(True, (0, ""), (0, ""))
  ],
  indirect=["__mock_os_path_exists", "__mock_run_shell_command"]
)
def test_returns_expected_result_when_loading_bashrc(
  __mock_os_path_exists,
  __mock_run_shell_command,
  expected_result
):
  result = ModeTestExecutor(__CONTEXT.copy())._ModeTestExecutor__load_bashrc()
  assert (
    result == expected_result
  ), get_assertion_message("load bashrc output", expected_result, result)

def test_calls_logger_if_param_is_tests_when_running_tests(
  __mock_logger,
  __mock_run_shell_command
):
  executor = ModeTestExecutor(
    {**__CONTEXT, params.PARAM_TEST_NAMES: __MULTIPLE_TESTS}
  )
  executor._ModeTestExecutor__run_tests()
  __mock_logger.assert_called_once_with(
    f" Tests to run: {', '.join(__MULTIPLE_TESTS)}"
  )

@pytest.mark.parametrize(
  "show_tests,all_funcs,all_programs",
  [
    pytest.param(True, False, False),
    pytest.param(False, True, False),
    pytest.param(False, False, True),
  ]
)
def test_does_not_call_logger_if_param_is_not_tests_when_running_tests(
  show_tests,
  all_funcs,
  all_programs,
  __mock_logger,
  __mock_run_shell_command
):
  executor = ModeTestExecutor(
    {
      **__CONTEXT,
      params.PARAM_TEST_NAMES: [],
      params.PARAM_SHOW_TESTS: show_tests,
      params.PARAM_ALL_FUNCTIONS: all_funcs,
      params.PARAM_ALL_PROGRAMS: all_programs
    }
  )
  executor._ModeTestExecutor__run_tests()
  __mock_logger.assert_not_called()

@pytest.mark.parametrize(
  "python_home,cuda,param,expected_no_cuda",
  [
    pytest.param(None, False, "--show", "--noCuda"),
    pytest.param(None, False, "--allFuncs", "--noCuda"),
    pytest.param(None, False, "--allPrograms", "--noCuda"),
    pytest.param(None, False, " ".join(__MULTIPLE_TESTS), "--noCuda"),
    pytest.param(None, True, "--show", ""),
    pytest.param(None, True, "--allFuncs", ""),
    pytest.param(None, True, "--allPrograms", ""),
    pytest.param(None, True, " ".join(__MULTIPLE_TESTS), ""),
    pytest.param(__PYHTON_HOME, False, "--show", "--noCuda"),
    pytest.param(__PYHTON_HOME, False, "--allFuncs", "--noCuda"),
    pytest.param(__PYHTON_HOME, False, "--allPrograms", "--noCuda"),
    pytest.param(__PYHTON_HOME, False, " ".join(__MULTIPLE_TESTS), "--noCuda"),
    pytest.param(__PYHTON_HOME, True, "--show", ""),
    pytest.param(__PYHTON_HOME, True, "--allFuncs", ""),
    pytest.param(__PYHTON_HOME, True, "--allPrograms", ""),
    pytest.param(__PYHTON_HOME, True, " ".join(__MULTIPLE_TESTS), "")
  ]
)
def test_calls_run_shell_command_when_running_tests(
  python_home,
  cuda,
  param,
  expected_no_cuda,
  __mock_run_shell_command,
  __mock_os_path_join,
  __mock_binaries_path,
  __mock_python_test_script_name,
  __mock_python_test_script_path
):
  new_context = {
    **__CONTEXT,
    variables.PYTHON_HOME: python_home,
    variables.CUDA: cuda
  }
  executor = ModeTestExecutor(new_context)
  executor.param_value = param
  executor._ModeTestExecutor__run_tests()
  __mock_run_shell_command.assert_called_once_with(
    f"{executor.python_home} {__mock_python_test_script_name} {param} {expected_no_cuda}",
    cwd=__mock_python_test_script_path,
    show_output=True,
    show_error=True
  )

@pytest.mark.parametrize(
  "__mock_run_shell_command",
  [pytest.param((0, "")), pytest.param((1, "error"))],
  indirect=["__mock_run_shell_command"]
)
def test_returns_expected_results_when_running_tests(
  __mock_run_shell_command
):
  output = ModeTestExecutor(__CONTEXT.copy())._ModeTestExecutor__run_tests()
  assert (
    output == __mock_run_shell_command()
  ), get_assertion_message("function output", __mock_run_shell_command(), output)

def test_calls_path_os_isdir_when_running_sync_operation(
  __mock_os_path_isdir,
  __mock_run_shell_command,
  __mock_dataset_path
):
  executor = ModeTestExecutor(__CONTEXT.copy())
  executor._sync_operation()
  __mock_os_path_isdir.assert_called_once_with(
    __mock_dataset_path
  )

@pytest.mark.parametrize(
  "__mock_os_path_isdir,expected_task",
  [
    pytest.param(False, "Downloading"),
    pytest.param(True, "Updating")
  ],
  indirect=["__mock_os_path_isdir"]
)
def test_calls_logger_when_running_sync_operation(
  __mock_os_path_isdir,
  expected_task,
  __mock_logger,
  __mock_logger_blue,
  __mock_run_shell_command,
  __mock_run_tests
):
  executor = ModeTestExecutor(__CONTEXT.copy())
  executor._sync_operation()
  __mock_logger.assert_called_once_with(
    __mock_logger_blue(f"{expected_task} the test files")
  )

@pytest.mark.parametrize(
  "__mock_os_path_isdir,expected_task,expected_show_output",
  [
    pytest.param(False, "download", True),
    pytest.param(True, "update", False)
  ],
  indirect=["__mock_os_path_isdir"]
)
def test_calls_run_shell_command_when_running_sync_operation(
  __mock_os_path_isdir,
  expected_task,
  expected_show_output,
  __mock_os_path_join,
  __mock_run_shell_command,
  __mock_run_tests,
  __mock_dataset_name,
  __mock_dataset_path
):
  executor = ModeTestExecutor(__CONTEXT.copy())
  executor._sync_operation()
  args = f"{__mock_dataset_path} {urls.SCIPION_TESTS_URL} {__mock_dataset_name}"
  sync_program_relative_path = __mock_os_path_join(
    ".",
    os.path.basename(executor.sync_program_path)
  )
  __mock_run_shell_command.assert_called_once_with(
    f"{sync_program_relative_path} {expected_task} {args}",
      cwd=os.path.dirname(executor.sync_program_path),
      show_output=expected_show_output
  )

def test_calls_load_bashrc_when_running_executor(
  __mock_load_bashrc,
  __mock_parent_run,
  __mock_run_tests
):
  ModeTestExecutor(__CONTEXT.copy()).run()
  __mock_load_bashrc.assert_called_once_with()

def test_calls_run_tests_if_parent_run_and_load_bash_succeed_when_running_executor(
  __mock_load_bashrc,
  __mock_parent_run,
  __mock_run_tests
):
  ModeTestExecutor(__CONTEXT.copy()).run()
  __mock_run_tests.assert_called_once_with()

@pytest.mark.parametrize(
  "__mock_load_bashrc,__mock_parent_run",
  [
    pytest.param((1, ""), (1, "")),
    pytest.param((1, ""), (0, "")),
    pytest.param((0, ""), (1, ""))
  ],
  indirect=["__mock_load_bashrc", "__mock_parent_run"]
)
def test_does_not_call_run_tests_if_parent_run_or_load_bash_fail_when_running_executor(
  __mock_load_bashrc,
  __mock_parent_run,
  __mock_run_tests
):
  ModeTestExecutor(__CONTEXT.copy()).run()
  __mock_run_tests.assert_not_called()

@pytest.mark.parametrize(
  "__mock_load_bashrc,__mock_sync_operation,__mock_run_tests,expected_result",
  [
    pytest.param(
      (1, "source error"), (2, "command error"), (3, "test error"), (1, "source error")
    ),
    pytest.param(
      (1, "source error"), (0, ""), (0, ""), (1, "source error")
    ),
    pytest.param((0, ""), (2, "command error"), (3, "test error"), (2, "command error")),
    pytest.param((0, ""), (2, "command error"), (0, ""), (2, "command error")),
    pytest.param((0, ""), (0, ""), (3, "test error"), (3, "test error")),
    pytest.param((0, ""), (0, ""), (0, ""), (0, ""))
  ],
  indirect=["__mock_load_bashrc", "__mock_sync_operation", "__mock_run_tests"]
)
def test_returns_expected_result(
  __mock_load_bashrc,
  __mock_sync_operation,
  __mock_run_tests,
  expected_result,
  __mock_os_path_exists
):
  result = ModeTestExecutor(__CONTEXT.copy()).run()
  assert (
    result == expected_result
  ), get_assertion_message("sync result", expected_result, result)

@pytest.fixture(autouse=True)
def __mock_binaries_path():
  with patch.object(
    paths,
    "BINARIES_PATH",
    __BINARIES_PATH
  ) as mock_object:
    yield mock_object

@pytest.fixture(autouse=True)
def __mock_os_path_join():
  with patch("os.path.join") as mock_method:
    mock_method.side_effect = lambda *args: '/'.join([*args])
    yield mock_method

@pytest.fixture(autouse=True)
def __mock_logger():
  with patch(
    "xmipp3_installer.application.logger.logger.Logger.__call__"
  ) as mock_method:
    yield mock_method

@pytest.fixture(params=[(0, "")])
def __mock_run_shell_command(request):
  with patch(
    "xmipp3_installer.installer.handlers.shell_handler.run_shell_command"
  ) as mock_method:
    mock_method.return_value = request.param
    yield mock_method

@pytest.fixture(autouse=True)
def __mock_logger_blue():
  with patch(
    "xmipp3_installer.application.logger.logger.Logger.blue"
  ) as mock_method:
    mock_method.side_effect = lambda text: f"blue-{text}-blue"
    yield mock_method

@pytest.fixture(autouse=True, params=[False])
def __mock_os_path_isdir(request):
  with patch("os.path.isdir") as mock_method:
    mock_method.return_value = request.param
    yield mock_method

@pytest.fixture(params=[(0, "")])
def __mock_run_tests(request):
  with patch(
    "xmipp3_installer.installer.modes.mode_sync.mode_test_executor.ModeTestExecutor._ModeTestExecutor__run_tests"
  ) as mock_method:
    mock_method.return_value = request.param
    yield mock_method

@pytest.fixture(autouse=True)
def __mock_dataset_name():
  with patch.object(
    mode_test_executor,
    "_DATASET_NAME",
    __DATASET_NAME
  ) as mock_object:
    yield mock_object

@pytest.fixture(autouse=True)
def __mock_python_test_script_path():
  with patch.object(
    mode_test_executor,
    "_PYTHON_TEST_SCRIPT_PATH",
    __PYTHON_TEST_SCRIPT_PATH
  ) as mock_object:
    yield mock_object

@pytest.fixture(autouse=True)
def __mock_python_test_script_name():
  with patch.object(
    mode_test_executor,
    "_PYTHON_TEST_SCRIPT_NAME",
    __PYTHON_TEST_SCRIPT_NAME
  ) as mock_object:
    yield mock_object

@pytest.fixture(autouse=True)
def __mock_bashrc_file_path():
  with patch.object(
    mode_test_executor,
    "_BASHRC_FILE_PATH",
    _BASHRC_FILE_PATH
  ) as mock_object:
    yield mock_object

@pytest.fixture(autouse=True)
def __mock_dataset_path():
  with patch.object(
    mode_test_executor,
    "_DATASET_PATH",
    __DATASET_PATH
  ) as mock_object:
    yield mock_object

@pytest.fixture(params=[True])
def __mock_os_path_exists(request):
  with patch("os.path.exists") as mock_method:
    mock_method.return_value = request.param
    yield mock_method

@pytest.fixture(params=[(0, "")])
def __mock_sync_operation(request):
  with patch(
    "xmipp3_installer.installer.modes.mode_sync.mode_test_executor.ModeTestExecutor._sync_operation"
  ) as mock_method:
    mock_method.return_value = request.param
    yield mock_method

@pytest.fixture(params=[(0, "")])
def __mock_load_bashrc(request):
  with patch(
    "xmipp3_installer.installer.modes.mode_sync.mode_test_executor.ModeTestExecutor._ModeTestExecutor__load_bashrc"
  ) as mock_method:
    mock_method.return_value = request.param
    yield mock_method

@pytest.fixture(params=[(0, "")])
def __mock_parent_run(request):
  with patch(
    "xmipp3_installer.installer.modes.mode_sync.mode_sync_executor.ModeSyncExecutor.run"
  ) as mock_method:
    mock_method.return_value = request.param
    yield mock_method
