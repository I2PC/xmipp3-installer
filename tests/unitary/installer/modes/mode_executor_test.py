from abc import ABC
from unittest.mock import patch

import pytest

from xmipp3_installer.installer.modes.mode_executor import ModeExecutor
from xmipp3_installer.installer import constants

from .... import get_assertion_message

def test_is_instance_of_abstract_class(__dummy_test_mode_executor):
  executor = __dummy_test_mode_executor({})
  executor.run() # To cover dummy implementation execution
  assert (
    isinstance(executor, ABC)
  ), get_assertion_message(
    "parent class",
    ABC.__name__,
    executor.__class__.__bases__[0].__name__
  )

def test_raises_exception_when_run_method_not_implemented(
  __no_implementation_child
):
  with pytest.raises(TypeError):
    __no_implementation_child({})

def test_sets_args_attribute_in_initialization(__dummy_test_mode_executor):
  args = {"key": "value"}
  executor = __dummy_test_mode_executor(args)
  assert (
    executor.args == args
  ), get_assertion_message("args attribute", args, executor.args)

def test_sets_executor_default_config_without_override(__dummy_test_mode_executor):
  executor = __dummy_test_mode_executor({})
  assert (
    (
      executor.logs_to_file,
      executor.prints_with_substitution,
      executor.prints_banner_on_exit,
      executor.sends_installation_info
    ) == (False, False, False, False)
  ), get_assertion_message(
    "default executor configuration",
    (False, False, False, False),
    (
      executor.logs_to_file,
      executor.prints_with_substitution,
      executor.prints_banner_on_exit,
      executor.sends_installation_info
    )
  )

@pytest.mark.parametrize(
  "__configured_mode_executor,expected_configuration",
  [
    pytest.param((False, False, False, False), (False, False, False, False)),
    pytest.param((False, False, False, True), (False, False, False, True)),
    pytest.param((False, False, True, False), (False, False, True, False)),
    pytest.param((False, False, True, True), (False, False, True, True)),
    pytest.param((False, True, False, False), (False, True, False, False)),
    pytest.param((False, True, False, True), (False, True, False, True)),
    pytest.param((False, True, True, False), (False, True, True, False)),
    pytest.param((False, True, True, True), (False, True, True, True)),
    pytest.param((True, False, False, False), (True, False, False, False)),
    pytest.param((True, False, False, True), (True, False, False, True)),
    pytest.param((True, False, True, False), (True, False, True, False)),
    pytest.param((True, False, True, True), (True, False, True, True)),
    pytest.param((True, True, False, False), (True, True, False, False)),
    pytest.param((True, True, False, True), (True, True, False, True)),
    pytest.param((True, True, True, False), (True, True, True, False)),
    pytest.param((True, True, True, True), (True, True, True, True))
  ],
  indirect=["__configured_mode_executor"]
)
def test_sets_expected_executor_config_with_override(
  __configured_mode_executor,
  expected_configuration,
  __mock_logger_start_log_file
):
  executor = __configured_mode_executor({})
  assert (
    (
      executor.logs_to_file,
      executor.prints_with_substitution,
      executor.prints_banner_on_exit,
      executor.sends_installation_info
    ) == expected_configuration
  ), get_assertion_message(
    "default executor configuration",
    expected_configuration,
    (
      executor.logs_to_file,
      executor.prints_with_substitution,
      executor.prints_banner_on_exit,
      executor.sends_installation_info
    )
  )

def test_does_not_call_logger_start_log_file_with_default_configuration(
  __dummy_test_mode_executor,
  __mock_logger_start_log_file
):
  __dummy_test_mode_executor({})
  __mock_logger_start_log_file.assert_not_called()

@pytest.mark.parametrize(
  "__configured_mode_executor",
  [
    pytest.param((True, False, False, False))
  ],
  indirect=["__configured_mode_executor"]
)
def test_calls_logger_start_log_file_with_modified_configuration(
  __configured_mode_executor,
  __mock_logger_start_log_file
):
  __configured_mode_executor({})
  __mock_logger_start_log_file.assert_called_once_with(constants.LOG_FILE)

def test_does_not_call_logger_set_allow_substitution_with_default_configuration(
  __dummy_test_mode_executor,
  __mock_logger_set_allow_substitution
):
  __dummy_test_mode_executor({})
  __mock_logger_set_allow_substitution.assert_not_called()

@pytest.mark.parametrize(
  "__configured_mode_executor",
  [
    pytest.param((False, True, False, False))
  ],
  indirect=["__configured_mode_executor"]
)
def test_calls_logger_set_allow_substitution_with_modified_configuration(
  __configured_mode_executor,
  __mock_logger_set_allow_substitution
):
  __configured_mode_executor({})
  __mock_logger_set_allow_substitution.assert_called_once_with(True)

@pytest.fixture
def __no_implementation_child():
  class DummyModeExecutor(ModeExecutor):
    pass
  return DummyModeExecutor

@pytest.fixture
def __dummy_test_mode_executor():
  class TestExecutor(ModeExecutor):
    def run(self):
      return (0, "")
  return TestExecutor

@pytest.fixture(params=[(False, False, False, False)])
def __configured_mode_executor(__dummy_test_mode_executor, request):
  logs_to_file, substitute, prints_banner, sends_info = request.param
  class ConfiguredModeExecutor(__dummy_test_mode_executor):
    def _set_executor_config(self):
      self.logs_to_file = logs_to_file
      self.prints_with_substitution = substitute
      self.prints_banner_on_exit = prints_banner
      self.sends_installation_info = sends_info
  return ConfiguredModeExecutor

@pytest.fixture
def __mock_logger_start_log_file():
  with patch(
    "xmipp3_installer.application.logger.logger.Logger.start_log_file"
  ) as mock_method:
    yield mock_method

@pytest.fixture
def __mock_logger_set_allow_substitution():
  with patch(
    "xmipp3_installer.application.logger.logger.Logger.set_allow_substitution"
  ) as mock_method:
    yield mock_method
