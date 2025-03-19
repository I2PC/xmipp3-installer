from unittest.mock import patch

import pytest

from xmipp3_installer.installer.constants import paths
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
  clean_all_executor = ModeCleanAllExecutor({})
  base_config = (
    base_executor.logs_to_file,
    base_executor.prints_with_substitution,
    base_executor.prints_banner_on_exit,
    base_executor.sends_installation_info
  )
  inherited_config = (
    clean_all_executor.logs_to_file,
    clean_all_executor.prints_with_substitution,
    clean_all_executor.prints_banner_on_exit,
    clean_all_executor.sends_installation_info
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

def test_returns_expected_paths_to_delete():
  paths_to_delete = ModeCleanAllExecutor({})._get_paths_to_delete()
  expected_paths = [
    *paths.XMIPP_SOURCE_PATHS,
    paths.INSTALL_PATH,
    paths.BUILD_PATH,
    paths.CONFIG_FILE
  ]
  assert (
    paths_to_delete == expected_paths
  ), get_assertion_message("paths to delete", expected_paths, paths_to_delete)

@pytest.fixture
def __dummy_test_mode_clean_executor():
  class TestExecutor(ModeCleanExecutor):
    def _get_paths_to_delete(self):
      return []
    def _get_confirmation_message(self):
      return ""
    def _get_confirmation_keyword(self):
      return ""
  # For coverage
  executor = TestExecutor({})
  executor._get_paths_to_delete()
  executor._get_confirmation_message()
  executor._get_confirmation_keyword()
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
