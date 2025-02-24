import os
from unittest.mock import patch

import pytest

from xmipp3_installer.application.cli.arguments import params
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
	variables.CUDA: True
}
__PYHTON_HOME = "/path/to/python"
__DATASET_PATH = "/path/to/dataset"
__DATASET_NAME = "dataset_name"
__PYTHON_TEST_SCRIPT_PATH = "/path/to/python_script"
__PYTHON_TEST_SCRIPT_NAME = "script_name"

def test_implements_interface_mode_sync_executor():
	executor = ModeTestExecutor(__CONTEXT.copy())
	assert (
		isinstance(executor, mode_sync_executor.ModeSyncExecutor)
	), get_assertion_message(
		"parent class",
		mode_sync_executor.ModeSyncExecutor.__name__,
		executor.__class__.__bases__[0].__name__
	)

def test_sets_expected_values_when_initializing():
	executor = ModeTestExecutor(__CONTEXT.copy())
	values = (
		executor.test_names,
		executor.cuda,
		executor.show
	)
	expected_values = (
		__MULTIPLE_TESTS,
		True,
		False
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

def test_calls_logger_when_running_tests(
	__mock_logger,
	__mock_run_shell_command
):
	executor = ModeTestExecutor(__CONTEXT.copy())
	executor._ModeTestExecutor__run_tests()
	__mock_logger.assert_called_once_with(
		f" Tests to run: {', '.join(__MULTIPLE_TESTS)}"
	)

@pytest.mark.parametrize(
	"python_home,cuda,show,expected_no_cuda,expected_show",
	[
		pytest.param(None, False, False, "--noCuda", ""),
		pytest.param(None, False, True, "--noCuda", "--show"),
		pytest.param(None, True, False, "", ""),
		pytest.param(None, True, True, "", "--show"),
		pytest.param(__PYHTON_HOME, False, False, "--noCuda", ""),
		pytest.param(__PYHTON_HOME, False, True, "--noCuda", "--show"),
		pytest.param(__PYHTON_HOME, True, False, "", ""),
		pytest.param(__PYHTON_HOME, True, True, "", "--show")
	]
)
def test_calls_run_shell_command_when_running_tests(
	python_home,
	cuda,
	show,
	expected_no_cuda,
	expected_show,
	__mock_run_shell_command,
	__mock_os_path_join,
	__mock_binaries_path,
	__mock_python_test_script_name,
	__mock_python_test_script_path
):
	new_context = {
		**__CONTEXT,
		variables.PYTHON_HOME: python_home,
		variables.CUDA: cuda,
		params.PARAM_SHOW_TESTS: show
	}
	executor = ModeTestExecutor(new_context)
	executor._ModeTestExecutor__run_tests()
	__mock_run_shell_command.assert_called_once_with(
		f"{executor.python_home} {__mock_python_test_script_name} {' '.join(__MULTIPLE_TESTS)} {expected_no_cuda}{expected_show}",
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

@pytest.mark.parametrize(
	"__mock_sync_operation,__mock_run_tests,expected_result",
	[
		pytest.param((1, "command error"), (2, "test error"), (1, "command error")),
		pytest.param((1, "command error"), (0, ""), (1, "command error")),
		pytest.param((0, ""), (2, "test error"), (2, "test error")),
		pytest.param((0, ""), (0, ""), (0, ""))
	],
	indirect=["__mock_sync_operation", "__mock_run_tests"]
)
def test_returns_expected_result(
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
def __mock_dataset_path():
	with patch.object(
		mode_test_executor,
		"_DATASET_PATH",
		__DATASET_PATH
	) as mock_object:
		yield mock_object

@pytest.fixture
def __mock_os_path_exists():
	with patch("os.path.exists") as mock_method:
		mock_method.return_value = True
		yield mock_method

@pytest.fixture(params=[(0, "")])
def __mock_sync_operation(request):
	with patch(
		"xmipp3_installer.installer.modes.mode_sync.mode_test_executor.ModeTestExecutor._sync_operation"
	) as mock_method:
		mock_method.return_value = request.param
		yield mock_method
