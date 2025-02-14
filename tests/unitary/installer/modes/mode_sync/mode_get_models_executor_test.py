import pytest
from unittest.mock import patch, call

from xmipp3_installer.installer import constants, urls
from xmipp3_installer.installer.modes.mode_sync import mode_sync_executor
from xmipp3_installer.installer.modes.mode_sync.mode_get_models_executor import ModeGetModelsExecutor

from ..... import get_assertion_message

__MODELS_DIR = "/path/to/models"
__ARGS = {
	'directory': __MODELS_DIR
}
__SYNC_PROGRAM_PATH = "/path/to/sync/program"
__SYNC_PROGRAM_NAME = "sync_name"

def test_implements_interface_mode_sync_executor():
	executor = ModeGetModelsExecutor(__ARGS.copy())
	assert (
		isinstance(executor, mode_sync_executor.ModeSyncExecutor)
	), get_assertion_message(
		"parent class",
		mode_sync_executor.ModeSyncExecutor.__name__,
		executor.__class__.__bases__[0].__name__
	)

def test_sets_dist_path_when_initializing(
	__mock_sources_path,
	__mock_xmipp_name,
	__mock_os_path_join
):
	executor = ModeGetModelsExecutor(__ARGS.copy())
	expected_dist_path = __mock_os_path_join(__mock_sources_path, __mock_xmipp_name)
	assert (
		executor.dist_path == expected_dist_path
	), get_assertion_message("dist path", expected_dist_path, executor.dist_path)

@pytest.mark.parametrize(
	"input_directory,expected_directory",
	[
		pytest.param("some-directory", "some-directory"),
		pytest.param(
			f"{constants.SOURCES_PATH}/{constants.XMIPP}",
			f"{constants.SOURCES_PATH}/{constants.XMIPP}/models"
		)
	]
)
def test_sets_models_directory_when_initializing(
	input_directory,
	expected_directory
):
	executor = ModeGetModelsExecutor({**__ARGS, "directory": input_directory})
	assert (
		executor.models_directory == expected_directory
	), get_assertion_message("models directory", expected_directory, executor.models_directory)

@pytest.mark.parametrize(
	"__mock_run_shell_command",
	[pytest.param((0, "")), pytest.param((1, "error"))],
	indirect=["__mock_run_shell_command"]
)
def test_calls_logger_with_download_when_executing_model_operation(
	__mock_os_path_exists,
	__mock_os_path_isdir,
	__mock_logger,
	__mock_logger_green,
	__mock_run_shell_command
):
	__mock_os_path_isdir.return_value = False
	ModeGetModelsExecutor(__ARGS.copy()).run()
	expected_calls = [
		call("Downloading Deep Learning models (in background)")
	]
	if __mock_run_shell_command()[0] == 0:
		expected_calls.append(
			call(__mock_logger_green("Models successfully downloaded!"))
		)
	__mock_logger.assert_has_calls(expected_calls)
	assert (
		__mock_logger.call_count == len(expected_calls)
	), get_assertion_message("call count", expected_calls, __mock_logger.call_count)

@pytest.mark.parametrize(
	"__mock_run_shell_command",
	[pytest.param((0, "")), pytest.param((1, "error"))],
	indirect=["__mock_run_shell_command"]
)
def test_calls_logger_with_update_when_executing_model_operation(
	__mock_os_path_exists,
	__mock_os_path_isdir,
	__mock_logger,
	__mock_logger_green,
	__mock_run_shell_command
):
	ModeGetModelsExecutor(__ARGS.copy()).run()
	expected_calls = [
		call("Updating Deep Learning models (in background)")
	]
	if __mock_run_shell_command()[0] == 0:
		expected_calls.append(
			call(__mock_logger_green("Models successfully updated!"))
		)
	__mock_logger.assert_has_calls(expected_calls)
	assert (
		__mock_logger.call_count == len(expected_calls)
	), get_assertion_message("call count", expected_calls, __mock_logger.call_count)

@pytest.mark.parametrize(
	"__mock_os_path_isdir,expected_task",
	[pytest.param(False, "download"), pytest.param(True, "update")],
	indirect=["__mock_os_path_isdir"]
)
def test_calls_run_shell_command_when_executing_model_operation(
	__mock_os_path_exists,
	__mock_os_path_isdir,
	__mock_logger,
	__mock_logger_green,
	__mock_run_shell_command,
	__mock_sync_program_path,
	__mock_sync_program_name,
	__mock_os_path_join,
	expected_task
):
	ModeGetModelsExecutor(__ARGS.copy()).run()
	sync_program = __mock_os_path_join(
		__mock_sync_program_path,
		__mock_sync_program_name
	)
	__mock_run_shell_command.assert_called_once_with(
		f"{sync_program} {expected_task} {__MODELS_DIR} {urls.MODELS_URL} DLmodels",
		show_command=True,
		show_output=True,
		show_error=True
	)

@pytest.fixture(autouse=True)
def __mock_logger():
	with patch(
		"xmipp3_installer.application.logger.logger.Logger.__call__"
	) as mock_method:
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_os_path_exists():
	with patch("os.path.exists") as mock_method:
		mock_method.return_value = True
		yield mock_method

@pytest.fixture(autouse=True, params=[True])
def __mock_os_path_isdir(request):
	with patch("os.path.isdir") as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(params=[(0, "")])
def __mock_run_shell_command(request):
	with patch(
		"xmipp3_installer.installer.handlers.shell_handler.run_shell_command"
	) as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture
def __mock_sources_path():
	with patch.object(
		constants, "SOURCES_PATH", "sources_path"
	) as mock_object:
		yield mock_object

@pytest.fixture
def __mock_xmipp_name():
	with patch.object(
		constants, "XMIPP", "test_xmipp"
	) as mock_object:
		yield mock_object

@pytest.fixture(autouse=True)
def __mock_os_path_join():
	with patch("os.path.join") as mock_method:
		mock_method.side_effect = lambda *args: '/'.join([*args])
		yield mock_method

@pytest.fixture
def __mock_logger_green():
  with patch(
    "xmipp3_installer.application.logger.logger.Logger.green"
  ) as mock_method:
    mock_method.side_effect = lambda text: f"green-{text}-green"
    yield mock_method

@pytest.fixture(autouse=True)
def __mock_sync_program_path():
	with patch.object(
		mode_sync_executor,
		"_SYNC_PROGRAM_PATH",
		__SYNC_PROGRAM_PATH
	) as mock_object:
		yield mock_object

@pytest.fixture(autouse=True)
def __mock_sync_program_name():
	with patch.object(
		mode_sync_executor,
		"_SYNC_PROGRAM_NAME",
		__SYNC_PROGRAM_NAME
	) as mock_object:
		yield mock_object
