import tarfile
from unittest.mock import patch, MagicMock, call

import pytest

from xmipp3_installer.application.logger import errors
from xmipp3_installer.installer import constants
from xmipp3_installer.installer.modes import mode_add_model_executor
from xmipp3_installer.installer.modes.mode_add_model_executor import ModeAddModelExecutor
from xmipp3_installer.installer.modes.mode_executor import ModeExecutor

from .... import get_assertion_message

__LOGIN = "test@test.com"
__MODEL_PATH = "/path/to/mymodel"
__MODEL_DIRNAME = "/path/to"
__MODEL_NAME = "mymodel"
__TAR_NAME = f"xmipp_model_{__MODEL_NAME}.tgz"
__TAR_PATH = f"{__MODEL_DIRNAME}/{__TAR_NAME}"
__ARGS = {
	'login': __LOGIN,
	'modelPath': __MODEL_PATH
}
__READ_ERROR = tarfile.ReadError("could not read")
__COMPRESSION_ERROR = tarfile.CompressionError("could not compress")
__RETURN_VALUES_STR = "return values"

def test_implements_interface_mode_executor():
	executor = ModeAddModelExecutor(__ARGS.copy())
	assert (
		isinstance(executor, ModeExecutor)
	), get_assertion_message(
		"parent class",
		ModeExecutor.__name__,
		executor.__class__.__bases__[0].__name__
	)

def test_sets_update_value_false_when_not_provided():
	executor = ModeAddModelExecutor(__ARGS.copy())
	assert (
		executor.update == False
	), get_assertion_message("update value", False, executor.update)

@pytest.mark.parametrize(
	"update",
	[pytest.param(False), pytest.param(True)]
)
def test_sets_update_values_when_initializing(update):
	executor = ModeAddModelExecutor({**__ARGS, 'update': update})
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
	expected_model_name
):
	executor = ModeAddModelExecutor({**__ARGS, 'modelPath': model_path})
	expected_tar_name = f"xmipp_model_{expected_model_name}.tgz"
	expected_tar_path = f"{expected_model_dir}/{expected_tar_name}"
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

def test_does_not_override_parent_config_values(__dummy_test_mode_executor):
	base_executor = __dummy_test_mode_executor({})
	base_executor.run()  # To cover dummy implementation execution
	add_model_executor = ModeAddModelExecutor(__ARGS.copy())
	base_config = (
		base_executor.logs_to_file,
		base_executor.prints_with_substitution,
		base_executor.prints_banner_on_exit
	)
	inherited_config = (
		add_model_executor.logs_to_file,
		add_model_executor.prints_with_substitution,
		add_model_executor.prints_banner_on_exit
	)
	assert (
		inherited_config == base_config
	), get_assertion_message("config values", base_config, inherited_config)

def test_calls_logger_when_generating_compressed_file(
	__mock_logger,
	__mock_tarfile_open
):
	executor = ModeAddModelExecutor(__ARGS.copy())
	executor._ModeAddModelExecutor__generate_compressed_file()
	__mock_logger.assert_called_once_with(f"Creating the {__TAR_NAME} model.")

def test_calls_tarfile_open_when_generating_compressed_file(__mock_tarfile_open):
	executor = ModeAddModelExecutor(__ARGS.copy())
	executor._ModeAddModelExecutor__generate_compressed_file()
	__mock_tarfile_open.assert_called_once_with(__TAR_PATH, "w:gz")

def test_calls_tarfile_add_when_generating_compressed_file(__mock_tarfile_open):
	executor = ModeAddModelExecutor(__ARGS.copy())
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
	executor = ModeAddModelExecutor(__ARGS.copy())
	return_values = executor._ModeAddModelExecutor__generate_compressed_file()
	assert (
		return_values == expected_return_values
	), get_assertion_message(__RETURN_VALUES_STR, expected_return_values, return_values)

def test_calls_logger_when_getting_confirmation(
	__mock_logger,
	__mock_logger_yellow
):
	executor = ModeAddModelExecutor(__ARGS.copy())
	executor._ModeAddModelExecutor__get_confirmation()
	expected_text = __mock_logger_yellow("Warning: Uploading, please BE CAREFUL! This can be dangerous.")
	expected_text += f"\nYou are going to be connected to {__LOGIN} to write in folder {constants.SCIPION_SOFTWARE_EM}."
	expected_text += "\nContinue? YES/no (case sensitive)"
	__mock_logger.assert_called_once_with(expected_text)

def test_calls_input_when_getting_confirmation(__mock_input):
	executor = ModeAddModelExecutor(__ARGS.copy())
	executor._ModeAddModelExecutor__get_confirmation()
	__mock_input.assert_called_once_with()

@pytest.mark.parametrize(
	"__mock_input,expected_confirmation",
	[
		pytest.param("NO", False),
		pytest.param("", False),
		pytest.param("yes", False),
		pytest.param("YES", True)
	],
	indirect=["__mock_input"]
)
def test_returns_expected_confirmation_result(
	__mock_input,
	expected_confirmation
):
	executor = ModeAddModelExecutor(__ARGS.copy())
	confirmation = executor._ModeAddModelExecutor__get_confirmation()
	assert (
		confirmation == expected_confirmation
	), get_assertion_message("confirmation value", expected_confirmation, confirmation)

def test_calls_os_abspath_when_uploading_model(
	__mock_os_path_abspath,
	__mock_run_shell_command
):
	executor = ModeAddModelExecutor(__ARGS.copy())
	executor._ModeAddModelExecutor__upload_model()
	__mock_os_path_abspath.assert_called_once_with(__TAR_PATH)

@pytest.mark.parametrize(
	"update,expected_update_str",
	[pytest.param(False, ""), pytest.param(True, "--update")]
)
def test_calls_run_shell_command_when_uploading_model(
	update,
	expected_update_str,
	__mock_run_shell_command,
	__mock_os_path_abspath,
	__mock_sync_program_path,
	__mock_os_path_join
):
	executor = ModeAddModelExecutor({**__ARGS, 'update': update})
	executor._ModeAddModelExecutor__upload_model()
	args = ', '.join([
		__LOGIN,
		__mock_os_path_abspath(__TAR_PATH),
		constants.SCIPION_SOFTWARE_EM,
		expected_update_str
	])
	expected_relative_call_path = __mock_os_path_join(".", mode_add_model_executor._SYNC_PROGRAM_NAME)
	__mock_run_shell_command.assert_called_once_with(
		f"{expected_relative_call_path} upload {args}",
		cwd=__mock_sync_program_path
	)

def test_calls_os_remove_when_upload_is_ok_when_uploading_model(
	__mock_run_shell_command,
	__mock_os_remove
):
	executor = ModeAddModelExecutor(__ARGS.copy())
	executor._ModeAddModelExecutor__upload_model()
	__mock_os_remove.assert_called_once_with(__TAR_PATH)

def test_does_not_call_os_remove_when_upload_is_not_ok(
	__mock_run_shell_command,
	__mock_os_remove
):
	__mock_run_shell_command.return_value = (1, "")
	executor = ModeAddModelExecutor(__ARGS.copy())
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
	executor = ModeAddModelExecutor(__ARGS.copy())
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
	executor = ModeAddModelExecutor(__ARGS.copy())
	return_values = executor._ModeAddModelExecutor__upload_model()
	assert (
		return_values == expected_results
	), get_assertion_message(__RETURN_VALUES_STR, expected_results, return_values)

def test_calls_logger_if_model_path_is_not_dir_when_running_executor(
	__mock_os_path_isdir,
	__mock_logger,
	__mock_logger_red
):
	__mock_os_path_isdir.return_value = False
	executor = ModeAddModelExecutor(__ARGS.copy())
	executor.run()
	error_message = __mock_logger_red(f"{__MODEL_PATH} is not a directory. Please, check the path.")
	error_message += "\n"
	error_message += __mock_logger_red("The name of the model will be the name of that folder.")
	__mock_logger.assert_called_once_with(error_message)

def test_calls_logger_if_sync_program_path_does_not_exist_when_running_executor(
	__mock_os_path_exists,
	__mock_logger,
	__mock_logger_red,
	__mock_os_path_join,
	__mock_sync_program_path
):
	__mock_os_path_exists.return_value = False
	executor = ModeAddModelExecutor(__ARGS.copy())
	executor.run()
	expected_full_path = __mock_os_path_join(__mock_sync_program_path, mode_add_model_executor._SYNC_PROGRAM_NAME)
	error_message = __mock_logger_red(f"{expected_full_path} does not exist.")
	error_message += "\n"
	error_message += __mock_logger_red("Xmipp needs to be compiled successfully before running this command!")
	__mock_logger.assert_called_once_with(error_message)

@pytest.mark.parametrize(
	"__mock_os_path_isdir,__mock_os_path_exists,__mock_generate_compressed_file,"
	"__mock_get_confirmation,__mock_upload_model,expected_return_values",
	[
		pytest.param(
			False, False, (1, "compression error"), False, (1, "upload error"), (errors.IO_ERROR, ""),
		),
		pytest.param(
			False, True, (0, ""), True, (0, ""), (errors.IO_ERROR, ""),
		),
		pytest.param(
			True, False, (1, "compression error"), False, (1, "upload error"), (errors.IO_ERROR, ""),
		),
		pytest.param(
			True, False, (0, ""), True, (0, ""), (errors.IO_ERROR, ""),
		),
		pytest.param(
			True, True, (1, "compression error"), False, (1, "upload error"), (1, "compression error"),
		),
		pytest.param(
			True, True, (1, "compression error"), (0, ""), True, (1, "compression error"),
		),
		pytest.param(
			True, True, (0, ""), False, (1, "upload error"), (errors.INTERRUPTED_ERROR, ""),
		),
		pytest.param(
			True, True, (0, ""), False, (0, ""), (errors.INTERRUPTED_ERROR, ""),
		),
		pytest.param(
			True, True, (0, ""), True, (1, "upload error"), (1, "upload error"),
		),
		pytest.param(
			True, True, (0, ""), True, (0, "upload ok"), (0, "upload ok"),
		)
	],
	indirect=[
		"__mock_os_path_isdir",
		"__mock_os_path_exists",
		"__mock_generate_compressed_file",
		"__mock_get_confirmation",
		"__mock_upload_model"
	]
)
def test_returns_expected_values_when_running_executor(
	__mock_os_path_isdir,
	__mock_os_path_exists,
	__mock_generate_compressed_file,
	__mock_get_confirmation,
	__mock_upload_model,
	expected_return_values
):
	executor = ModeAddModelExecutor(__ARGS.copy())
	return_values = executor.run()
	assert (
		return_values == expected_return_values
	), get_assertion_message(__RETURN_VALUES_STR, expected_return_values, return_values)

def __raise_tarfile_exception(is_read_error):
	if is_read_error:
		raise __READ_ERROR
	raise __COMPRESSION_ERROR

@pytest.fixture(autouse=True)
def __mock_os_path_join():
	with patch("os.path.join") as mock_method:
		mock_method.side_effect = lambda *args: '/'.join([*args])
		yield mock_method

@pytest.fixture
def __dummy_test_mode_executor():
	class TestExecutor(ModeExecutor):
		def run(self):
			return (0, "")
	return TestExecutor

@pytest.fixture(autouse=True)
def __mock_logger():
	with patch(
		"xmipp3_installer.application.logger.logger.Logger.__call__"
	) as mock_method:
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

@pytest.fixture(autouse=True)
def __mock_logger_red():
	with patch(
		"xmipp3_installer.application.logger.logger.Logger.red"
	) as mock_method:
		mock_method.side_effect = lambda text: f"red-{text}-red"
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

@pytest.fixture(params=["YES"], autouse=True)
def __mock_input(request):
	with patch("builtins.input") as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_os_path_abspath():
	with patch("os.path.abspath") as mock_method:
		mock_method.side_effect = lambda path: f"abs-{path}-abs"
		yield mock_method

@pytest.fixture(params=[(0, "")])
def __mock_run_shell_command(request):
  with patch(
    "xmipp3_installer.installer.handlers.shell_handler.run_shell_command"
  ) as mock_method:
    mock_method.return_value = request.param
    yield mock_method

@pytest.fixture(autouse=True)
def __mock_os_remove():
	with patch("os.remove") as mock_method:
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_sync_program_path(__mock_os_path_join):
	with patch.object(
		mode_add_model_executor,
		"_SYNC_PROGRAM_PATH",
		"./dist/bin"
	) as mock_object:
		yield mock_object

@pytest.fixture(autouse=True, params=[True])
def __mock_os_path_isdir(request):
	with patch("os.path.isdir") as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(params=[True])
def __mock_os_path_exists(request):
	with patch("os.path.exists") as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(params=[(0, "")])
def __mock_generate_compressed_file(request):
	with patch(
		"xmipp3_installer.installer.modes.mode_add_model_executor.ModeAddModelExecutor._ModeAddModelExecutor__generate_compressed_file"
	) as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(params=[True])
def __mock_get_confirmation(request):
	with patch(
		"xmipp3_installer.installer.modes.mode_add_model_executor.ModeAddModelExecutor._ModeAddModelExecutor__get_confirmation"
	) as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(params=[(0, "")])
def __mock_upload_model(request):
	with patch(
		"xmipp3_installer.installer.modes.mode_add_model_executor.ModeAddModelExecutor._ModeAddModelExecutor__upload_model"
	) as mock_method:
		mock_method.return_value = request.param
		yield mock_method
