import tarfile
from unittest.mock import patch, MagicMock

import pytest

from xmipp3_installer.application.logger import errors
from xmipp3_installer.installer import constants
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
	), get_assertion_message("return values", expected_return_values, return_values)

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
