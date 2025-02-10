from unittest.mock import patch

import pytest

from xmipp3_installer.installer import constants
from xmipp3_installer.installer.modes.mode_clean.mode_clean_executor import ModeCleanExecutor
from xmipp3_installer.installer.modes.mode_clean.mode_clean_all_executor import ModeCleanAllExecutor

from ..... import get_assertion_message

def test_implements_interface_mode_clean_executor():
	executor = ModeCleanAllExecutor({})
	assert (
		isinstance(executor, ModeCleanExecutor)
	), get_assertion_message(
		"parent class",
		ModeCleanExecutor.__name__,
		executor.__class__.__bases__[0].__name__
	)

def test_does_not_override_parent_config_values(__dummy_test_mode_clean_executor):
	base_executor = __dummy_test_mode_clean_executor({})
	base_executor._get_paths_to_delete() # To cover dummy implementation execution
	base_executor._get_confirmation_message() # To cover dummy implementation execution
	base_executor._get_confirmation_keyword() # To cover dummy implementation execution
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

def test_returns_expected_confirmation_keyword():
	expected_keyword = "YeS"
	confirmation_keyword = ModeCleanAllExecutor({})._get_confirmation_keyword()
	assert (
		confirmation_keyword == expected_keyword
	), get_assertion_message("confirmation keyword", expected_keyword, confirmation_keyword)

def test_calls_get_confirmation_keyword_when_getting_confirmation_message(
	__mock_get_confirmation_keyword
):
	ModeCleanAllExecutor({})._get_confirmation_message()
	__mock_get_confirmation_keyword.assert_called_once_with()

def test_returns_expected_confirmation_message(
	__mock_get_confirmation_keyword,
	__mock_logger_yellow
):
	confirmation_message = ModeCleanAllExecutor({})._get_confirmation_message()
	expected_confirmation_message = __mock_logger_yellow(
		"WARNING: This will DELETE ALL content from src and build, and also the xmipp.conf file."
	)
	second_line = __mock_logger_yellow("\tNotice that if you have unpushed changes, they will be deleted.")
	third_line = __mock_logger_yellow(f"\nIf you are sure you want to do this, type '{__mock_get_confirmation_keyword()}' (case sensitive):")
	expected_confirmation_message += f"\n{second_line}\n{third_line}"
	assert (
		confirmation_message == expected_confirmation_message
	), get_assertion_message("confirmation message", expected_confirmation_message, confirmation_message)

def test_returns_expected_paths_to_delete(__mock_os_path_join):
	paths = ModeCleanAllExecutor({})._get_paths_to_delete()
	expected_paths = [
		__mock_os_path_join(constants.SOURCES_PATH, constants.XMIPP_CORE),
		constants.INSTALL_PATH,
		constants.BUILD_PATH,
		constants.CONFIG_FILE
	]
	assert (
		paths == expected_paths
	), get_assertion_message("paths to delete", expected_paths, paths)

@pytest.fixture
def __dummy_test_mode_clean_executor():
	class TestExecutor(ModeCleanExecutor):
		def _get_paths_to_delete(self):
			return []
		def _get_confirmation_message(self):
			return ""
		def _get_confirmation_keyword(self):
			return ""
	return TestExecutor

@pytest.fixture
def __mock_get_confirmation_keyword():
	with patch(
		"xmipp3_installer.installer.modes.mode_clean.mode_clean_all_executor.ModeCleanAllExecutor._get_confirmation_keyword"
	) as mock_method:
		mock_method.return_value = "confirmation keyword"
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_logger_yellow():
	with patch(
		"xmipp3_installer.application.logger.logger.Logger.yellow"
	) as mock_method:
		mock_method.side_effect = lambda text: f"yellow-{text}-yellow"
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_os_path_join():
	def __join_with_foward_slashes(*args):
		args = [arg.rstrip("/") for arg in args]
		return '/'.join([*args])
	with patch("os.path.join") as mock_method:
		mock_method.side_effect = __join_with_foward_slashes
		yield mock_method
