from unittest.mock import patch

import pytest

from xmipp3_installer.application.logger import errors
from xmipp3_installer.installer import constants
from xmipp3_installer.installer.modes.mode_executor import ModeExecutor
from xmipp3_installer.installer.modes.mode_clean_all_executor import ModeCleanAllExecutor

from .... import get_assertion_message

def test_implements_interface_mode_executor():
	executor = ModeCleanAllExecutor({})
	assert (
		isinstance(executor, ModeExecutor)
	), get_assertion_message(
		"parent class",
		ModeExecutor.__name__,
		executor.__class__.__bases__[0].__name__
	)

def test_does_not_override_parent_config_values(__dummy_test_mode_executor):
	base_executor = __dummy_test_mode_executor({})
	base_executor.run()  # To cover dummy implementation execution
	config_executor = ModeCleanAllExecutor({})
	base_config = (
		base_executor.logs_to_file,
		base_executor.prints_with_substitution,
		base_executor.prints_banner_on_exit
	)
	inherited_config = (
		config_executor.logs_to_file,
		config_executor.prints_with_substitution,
		config_executor.prints_banner_on_exit
	)
	assert (
		inherited_config == base_config
	), get_assertion_message("config values", base_config, inherited_config)

def test_calls_logger_when_getting_confirmation(
	__mock_logger,
	__mock_logger_yellow,
	__mock_get_user_confirmation
):
	ModeCleanAllExecutor._ModeCleanAllExecutor__get_confirmation()
	expected_message = __mock_logger_yellow(
		"WARNING: This will DELETE ALL content from src and build, and also the xmipp.conf file."
	)
	second_line_message = __mock_logger_yellow("\tNotice that if you have unpushed changes, they will be deleted.")
	third_line_message = __mock_logger_yellow("\nIf you are sure you want to do this, type 'YeS' (case sensitive):")
	expected_message += f"\n{second_line_message}\n{third_line_message}"
	__mock_logger.assert_called_once_with(expected_message)

def test_calls_get_user_confirmation_when_getting_confirmation(
	__mock_get_user_confirmation
):
	ModeCleanAllExecutor._ModeCleanAllExecutor__get_confirmation()
	__mock_get_user_confirmation.assert_called_once_with("YeS")

@pytest.mark.parametrize(
	"__mock_get_user_confirmation",
	[pytest.param(False), pytest.param(True)],
	indirect=["__mock_get_user_confirmation"]
)
def test_gets_expected_user_confirmation(
	__mock_get_user_confirmation
):
	confirmation = ModeCleanAllExecutor._ModeCleanAllExecutor__get_confirmation()
	assert (
		confirmation == __mock_get_user_confirmation()
	), get_assertion_message(
		"user confirmation",
		__mock_get_user_confirmation(),
		confirmation
	)

def test_returns_expected_paths_to_delete(__mock_os_path_join):
	paths = ModeCleanAllExecutor._ModeCleanAllExecutor__get_paths_to_delete()
	expected_paths = [
		*[
				__mock_os_path_join(constants.SOURCES_PATH, source)
				for source in constants.XMIPP_SOURCES
			],
			constants.INSTALL_PATH,
			constants.BUILD_PATH,
			constants.CONFIG_FILE
	]
	assert (
		paths == expected_paths
	), get_assertion_message("paths to delete", expected_paths, paths)

def test_calls_get_confirmation_when_running_executor(
	__mock_get_confirmation,
	__mock_get_paths_to_delete,
	__mock_logger
):
	ModeCleanAllExecutor({}).run()
	__mock_get_confirmation.assert_called_once_with()

def test_calls_get_paths_to_delete_when_running_executor(
	__mock_get_confirmation,
	__mock_get_paths_to_delete,
	__mock_logger
):
	ModeCleanAllExecutor({}).run()
	__mock_get_paths_to_delete.assert_called_once_with()

def test_calls_delete_paths_to_delete_when_running_executor(
	__mock_get_confirmation,
	__mock_get_paths_to_delete,
	__mock_delete_paths,
	__mock_logger
):
	ModeCleanAllExecutor({}).run()
	__mock_delete_paths.assert_called_once_with(__mock_get_paths_to_delete())

def test_calls_logger_when_running_executor(
	__mock_get_confirmation,
	__mock_get_paths_to_delete,
	__mock_delete_paths,
	__mock_logger,
	__mock_get_done_message
):
	ModeCleanAllExecutor({}).run()
	__mock_logger.assert_called_once_with(
		__mock_get_done_message()
	)

@pytest.mark.parametrize(
	"__mock_get_confirmation",
	[pytest.param(False), pytest.param(True)],
	indirect=["__mock_get_confirmation"]
)
def test_returns_expected_values_when_running_executor(
	__mock_get_confirmation,
	__mock_get_paths_to_delete,
	__mock_delete_paths,
	__mock_logger,
	__mock_get_done_message
):
	expected_values = (0, "") if __mock_get_confirmation() else (errors.INTERRUPTED_ERROR, "")
	values = ModeCleanAllExecutor({}).run()
	assert (
		values == expected_values
	), get_assertion_message("return values", expected_values, values)

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

@pytest.fixture(autouse=True, params=[True])
def __mock_get_user_confirmation(request):
	with patch(
		"xmipp3_installer.application.user_interactions.get_user_confirmation"
	) as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_os_path_join():
	def __join_with_foward_slashes(*args):
		args = [arg.rstrip("/") for arg in args]
		return '/'.join([*args])
	with patch("os.path.join") as mock_method:
		mock_method.side_effect = __join_with_foward_slashes
		yield mock_method

@pytest.fixture(params=[True])
def __mock_get_confirmation(request):
	with patch(
		"xmipp3_installer.installer.modes.mode_clean_all_executor.ModeCleanAllExecutor._ModeCleanAllExecutor__get_confirmation"
	) as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture
def __mock_get_paths_to_delete():
	with patch(
		"xmipp3_installer.installer.modes.mode_clean_all_executor.ModeCleanAllExecutor._ModeCleanAllExecutor__get_paths_to_delete"
	) as mock_method:
		mock_method.return_value = ["path1", "path2"]
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_delete_paths():
	with patch(
		"xmipp3_installer.repository.file_operations.delete_paths"
	) as mock_method:
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_get_done_message():
	with patch(
		"xmipp3_installer.application.logger.predefined_messages.get_done_message"
	) as mock_method:
		mock_method.return_value = "Done message"
		yield mock_method
