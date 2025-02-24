import os
import tarfile
from unittest.mock import patch, call, MagicMock

import pytest

from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.application.logger import errors
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.installer.modes.mode_sync import mode_sync_executor
from xmipp3_installer.installer.modes.mode_sync.mode_add_model_executor import ModeAddModelExecutor

from ..... import get_assertion_message

__LOGIN = "user@host"
__MODEL_PATH = "/path/to/mymodel"
__MODEL_DIRNAME = "/path/to"
__MODEL_NAME = "mymodel"
__TAR_NAME = f"xmipp_model_{__MODEL_NAME}.tgz"
__TAR_PATH = f"{__MODEL_DIRNAME}/{__TAR_NAME}"
__CONTEXT = {
	params.PARAM_LOGIN: __LOGIN,
	params.PARAM_MODEL_PATH: __MODEL_PATH,
	params.PARAM_UPDATE: False
}
__READ_ERROR = tarfile.ReadError("could not read")
__COMPRESSION_ERROR = tarfile.CompressionError("could not compress")
__RETURN_VALUES_STR = "return values"

def test_implements_interface_mode_sync_executor():
	executor = ModeAddModelExecutor(__CONTEXT.copy())
	assert (
		isinstance(executor, mode_sync_executor.ModeSyncExecutor)
	), get_assertion_message(
		"parent class",
		mode_sync_executor.ModeSyncExecutor.__name__,
		executor.__class__.__bases__[0].__name__
	)

@pytest.mark.parametrize(
	"missing_param",
	[
		pytest.param(params.PARAM_LOGIN),
		pytest.param(params.PARAM_MODEL_PATH),
		pytest.param(params.PARAM_UPDATE)
	]
)
def test_raises_key_error_when_expected_value_not_provided(missing_param):
	new_context = __CONTEXT.copy()
	del new_context[missing_param]
	with pytest.raises(KeyError):
		ModeAddModelExecutor(new_context)

@pytest.mark.parametrize(
	"update",
	[pytest.param(False), pytest.param(True)]
)
def test_sets_update_values_when_initializing(update):
	executor = ModeAddModelExecutor({**__CONTEXT, 'update': update})
	assert (
		executor.update == update
	), get_assertion_message("update value", update, executor.update)

@pytest.mark.parametrize(
	"model_path,expected_model_dir,expected_model_name",
	[
		pytest.param("", "", ""),
		pytest.param("/", "/", ""),
		pytest.param(__MODEL_NAME, "", __MODEL_NAME),
		pytest.param(__MODEL_PATH, __MODEL_DIRNAME, __MODEL_NAME)
	]
)
def test_sets_path_related_values_when_initializing(
	model_path,
	expected_model_dir,
	expected_model_name,
	__mock_os_path_join
):
	executor = ModeAddModelExecutor({**__CONTEXT, 'modelPath': model_path})
	expected_tar_name = f"xmipp_model_{expected_model_name}.tgz"
	expected_tar_path = __mock_os_path_join(expected_model_dir, expected_tar_name)
	received_values = [
		executor.model_dir,
		executor.model_name,
		executor.tar_file_name,
		executor.tar_file_path
	]
	expected_values = [
		expected_model_dir,
		expected_model_name,
		expected_tar_name,
		expected_tar_path
	]
	assert (
		received_values == expected_values
	), get_assertion_message("path related values", expected_values, received_values)

def test_calls_logger_when_generating_compressed_file(
	__mock_logger,
	__mock_tarfile_open
):
	executor = ModeAddModelExecutor(__CONTEXT.copy())
	executor._ModeAddModelExecutor__generate_compressed_file()
	__mock_logger.assert_called_once_with(f"Creating the {__TAR_NAME} model.")

def test_calls_tarfile_open_when_generating_compressed_file(__mock_tarfile_open):
	executor = ModeAddModelExecutor(__CONTEXT.copy())
	executor._ModeAddModelExecutor__generate_compressed_file()
	__mock_tarfile_open.assert_called_once_with(__TAR_PATH, "w:gz")

def test_calls_tarfile_add_when_generating_compressed_file(__mock_tarfile_open):
	executor = ModeAddModelExecutor(__CONTEXT.copy())
	executor._ModeAddModelExecutor__generate_compressed_file()
	__mock_tarfile_open.return_value.__enter__.return_value.add.assert_called_once_with(
		__MODEL_PATH,
		arcname=__MODEL_NAME
	)

@pytest.mark.parametrize(
	"__mock_tarfile_open,expected_return_values",
	[
		pytest.param((False, False), (0, "")),
		pytest.param((False, True), (0, "")),
		pytest.param((True, False), (errors.IO_ERROR, str(__COMPRESSION_ERROR))),
		pytest.param((True, True), (errors.IO_ERROR, str(__READ_ERROR)))
	],
	indirect=["__mock_tarfile_open"]
)
def test_returns_expected_outputs_when_generating_compressed_file(
	__mock_tarfile_open,
	expected_return_values
):
	executor = ModeAddModelExecutor(__CONTEXT.copy())
	return_values = executor._ModeAddModelExecutor__generate_compressed_file()
	assert (
		return_values == expected_return_values
	), get_assertion_message(__RETURN_VALUES_STR, expected_return_values, return_values)

def test_calls_logger_when_getting_confirmation(
	__mock_logger,
	__mock_logger_yellow
):
	executor = ModeAddModelExecutor(__CONTEXT.copy())
	executor._ModeAddModelExecutor__get_confirmation()
	expected_message = '\n'.join([
		__mock_logger_yellow("Warning: Uploading, please BE CAREFUL! This can be dangerous."),
		f"You are going to be connected to {__LOGIN} to write in folder {paths.SCIPION_SOFTWARE_EM}.",
		"Continue? YES/no (case sensitive)"
	])
	__mock_logger.assert_called_once_with(expected_message)

def test_calls_get_user_confirmation_when_getting_confirmation(
	__mock_get_user_confirmation
):
	executor = ModeAddModelExecutor(__CONTEXT.copy())
	executor._ModeAddModelExecutor__get_confirmation()
	__mock_get_user_confirmation.assert_called_once_with("YES")

def test_returns_get_user_confirmation_output_when_getting_confirmation(
	__mock_get_user_confirmation
):
	executor = ModeAddModelExecutor(__CONTEXT.copy())
	return_value = executor._ModeAddModelExecutor__get_confirmation()
	assert (
		return_value == __mock_get_user_confirmation.return_value
	), get_assertion_message(
		"confirmation output",
		__mock_get_user_confirmation.return_value,
		return_value
	)

@pytest.mark.parametrize(
	"update,expected_update_str",
	[pytest.param(False, ""), pytest.param(True, "--update")]
)
def test_calls_run_shell_command_when_uploading_model(
	update,
	expected_update_str,
	__mock_run_shell_command,
	__mock_os_path_join,
	__mock_os_path_abspath
):
	executor = ModeAddModelExecutor({**__CONTEXT, 'update': update})
	executor._ModeAddModelExecutor__upload_model()
	args = f"{__LOGIN}, {__mock_os_path_abspath(__TAR_PATH)}, {paths.SCIPION_SOFTWARE_EM}, {expected_update_str}"
	__mock_run_shell_command.assert_called_once_with(
		f"{__mock_os_path_join('.', os.path.basename(executor.sync_program_path))} upload {args}",
		cwd=os.path.dirname(executor.sync_program_path)
	)

def test_calls_os_remove_when_upload_is_ok_when_uploading_model(
	__mock_run_shell_command,
	__mock_os_remove
):
	executor = ModeAddModelExecutor(__CONTEXT.copy())
	executor._ModeAddModelExecutor__upload_model()
	__mock_os_remove.assert_called_once_with(__TAR_PATH)

def test_does_not_call_os_remove_when_upload_is_not_ok(
	__mock_run_shell_command,
	__mock_os_remove
):
	__mock_run_shell_command.return_value = (1, "")
	executor = ModeAddModelExecutor(__CONTEXT.copy())
	executor._ModeAddModelExecutor__upload_model()
	__mock_os_remove.assert_not_called()

@pytest.mark.parametrize(
	"__mock_run_shell_command",
	[
		pytest.param((0, "")),
		pytest.param((0, "whatever")),
		pytest.param((1, "")),
		pytest.param((1, "whatever"))
	],
	indirect=["__mock_run_shell_command"]
)
def test_calls_logger_deppending_on_upload_status(
	__mock_logger,
	__mock_logger_green,
	__mock_run_shell_command
):
	executor = ModeAddModelExecutor(__CONTEXT.copy())
	executor._ModeAddModelExecutor__upload_model()
	calls = [call(f"Trying to upload the model using {__LOGIN} as login")]
	if __mock_run_shell_command.return_value[0] == 0:
		calls.append(call(__mock_logger_green(f"{__MODEL_NAME} model successfully uploaded! Removing the local .tgz")))
	__mock_logger.assert_has_calls(calls)
	assert (
		__mock_logger.call_count == len(calls)
	), get_assertion_message("call count", len(calls), __mock_logger.call_count)

@pytest.mark.parametrize(
	"__mock_run_shell_command,expected_results",
	[
		pytest.param((0, ""), (0, "")),
		pytest.param((0, "whatever"), (0, "")),
		pytest.param((1, ""), (1, "")),
		pytest.param((1, "whatever"), (1, "whatever"))
	],
	indirect=["__mock_run_shell_command"]
)
def test_returns_expected_upload_output_status(
	__mock_run_shell_command,
	expected_results
):
	executor = ModeAddModelExecutor(__CONTEXT.copy())
	return_values = executor._ModeAddModelExecutor__upload_model()
	assert (
		return_values == expected_results
	), get_assertion_message(__RETURN_VALUES_STR, expected_results, return_values)

def test_calls_logger_if_model_path_is_not_dir_when_running_executor(
	__mock_os_path_isdir,
	__mock_logger,
	__mock_logger_red,
	__mock_os_path_exists
):
	__mock_os_path_isdir.return_value = False
	executor = ModeAddModelExecutor(__CONTEXT.copy())
	executor.run()
	error_message = __mock_logger_red(f"{__MODEL_PATH} is not a directory. Please, check the path.")
	error_message += "\n"
	error_message += __mock_logger_red("The name of the model will be the name of that folder.")
	__mock_logger.assert_called_once_with(error_message)

@pytest.mark.parametrize(
	"__mock_os_path_isdir,__mock_generate_compressed_file,"
	"__mock_get_confirmation,__mock_upload_model,expected_return_values",
	[
		pytest.param(
			False, (1, "compression error"), False, (1, "upload error"), (errors.IO_ERROR, ""),
		),
		pytest.param(
			False, (0, ""), True, (0, ""), (errors.IO_ERROR, ""),
		),
		pytest.param(
			True, (1, "compression error"), False, (1, "upload error"), (1, "compression error"),
		),
		pytest.param(
			True, (1, "compression error"), True, (0, ""), (1, "compression error"),
		),
		pytest.param(
			True, (0, ""), False, (1, "upload error"), (errors.INTERRUPTED_ERROR, ""),
		),
		pytest.param(
			True, (0, ""), False, (0, ""), (errors.INTERRUPTED_ERROR, ""),
		),
		pytest.param(
			True, (0, ""), True, (1, "upload error"), (1, "upload error"),
		),
		pytest.param(
			True, (0, ""), True, (0, ""), (0, ""),
		)
	],
	indirect=[
		"__mock_os_path_isdir",
		"__mock_generate_compressed_file",
		"__mock_get_confirmation",
		"__mock_upload_model"
	]
)
def test_returns_expected_values_when_running_executor(
	__mock_os_path_exists,
	__mock_os_path_isdir,
	__mock_generate_compressed_file,
	__mock_get_confirmation,
	__mock_upload_model,
	expected_return_values
):
	executor = ModeAddModelExecutor(__CONTEXT.copy())
	return_values = executor.run()
	assert (
		return_values == expected_return_values
	), get_assertion_message(__RETURN_VALUES_STR, expected_return_values, return_values)

def __raise_tarfile_exception(is_read_error):
	if is_read_error:
		raise __READ_ERROR
	raise __COMPRESSION_ERROR

@pytest.fixture(autouse=True)
def __mock_logger():
	with patch(
		"xmipp3_installer.application.logger.logger.Logger.__call__"
	) as mock_method:
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_logger_red():
	with patch(
		"xmipp3_installer.application.logger.logger.Logger.red"
	) as mock_method:
		mock_method.side_effect = lambda text: f"red-{text}-red"
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_logger_yellow():
	with patch(
		"xmipp3_installer.application.logger.logger.Logger.yellow"
	) as mock_method:
		mock_method.side_effect = lambda text: f"yellow-{text}-yellow"
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_logger_green():
	with patch(
		"xmipp3_installer.application.logger.logger.Logger.green"
	) as mock_method:
		mock_method.side_effect = lambda text: f"green-{text}-green"
		yield mock_method

@pytest.fixture(autouse=True, params=[True])
def __mock_os_path_isdir(request):
	with patch("os.path.isdir") as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(params=[(False, False)])
def __mock_tarfile_open(request):
	raises_exception = request.param[0]
	is_read_error = request.param[1]
	tar_file = MagicMock()
	if raises_exception:
		tar_file.add.side_effect = lambda *args, **kwargs: __raise_tarfile_exception(is_read_error)
	with patch("tarfile.open") as mock_method:
		mock_method.return_value.__enter__.return_value = tar_file
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_get_user_confirmation():
	with patch(
		"xmipp3_installer.application.user_interactions.get_user_confirmation"
	) as mock_method:
		mock_method.return_value = True
		yield mock_method

@pytest.fixture(params=[(0, "")])
def __mock_run_shell_command(request):
	with patch(
		"xmipp3_installer.installer.handlers.shell_handler.run_shell_command"
	) as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(params=[(0, "")])
def __mock_generate_compressed_file(request):
	with patch(
		"xmipp3_installer.installer.modes.mode_sync.mode_add_model_executor.ModeAddModelExecutor._ModeAddModelExecutor__generate_compressed_file"
	) as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(params=[True])
def __mock_get_confirmation(request):
	with patch(
		"xmipp3_installer.installer.modes.mode_sync.mode_add_model_executor.ModeAddModelExecutor._ModeAddModelExecutor__get_confirmation"
	) as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(params=[(0, "")])
def __mock_upload_model(request):
	with patch(
		"xmipp3_installer.installer.modes.mode_sync.mode_add_model_executor.ModeAddModelExecutor._ModeAddModelExecutor__upload_model"
	) as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_os_path_join():
	with patch("os.path.join") as mock_method:
		mock_method.side_effect = lambda *args: '/'.join([*args])
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_os_remove():
	with patch("os.remove") as mock_method:
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_os_path_abspath():
	with patch("os.path.abspath") as mock_method:
		mock_method.side_effect = lambda path: f"abs-{path}-abs"
		yield mock_method

@pytest.fixture(params=[True])
def __mock_os_path_exists(request):
	with patch("os.path.exists") as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_sync_program_path():
	with patch.object(
		mode_sync_executor,
		"_SYNC_PROGRAM_PATH",
		__MODEL_PATH
	) as mock_object:
		yield mock_object
