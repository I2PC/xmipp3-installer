import os
from unittest.mock import patch

import pytest

from xmipp3_installer.application.logger import errors
from xmipp3_installer.installer.modes import mode_executor
from xmipp3_installer.installer.modes.mode_sync import mode_sync_executor
from xmipp3_installer.installer.modes.mode_sync.mode_sync_executor import ModeSyncExecutor

from ..... import get_assertion_message

__SYNC_PROGRAM_PATH = os.path.join(
  mode_sync_executor._SYNC_PROGRAM_PATH,
  mode_sync_executor._SYNC_PROGRAM_NAME
)

class DummySyncExecutor(ModeSyncExecutor):
  def _sync_operation(self):
    return 0, ""

def test_is_instance_of_mode_executor():
  executor = DummySyncExecutor({})
  executor._sync_operation() # To cover dummy implementation
  assert (
    isinstance(executor, mode_executor.ModeExecutor)
  ), get_assertion_message(
    "parent class",
    mode_executor.ModeExecutor.__name__,
    executor.__class__.__bases__[0].__name__
  )

def test_raises_exception_when_execute_model_operation_not_implemented():
  with pytest.raises(TypeError):
    ModeSyncExecutor({})

def test_does_not_override_parent_config_values(
  __dummy_test_mode_executor
):
  base_executor = __dummy_test_mode_executor({})
  mode_sync_executor = DummySyncExecutor({})
  base_config = (
    base_executor.logs_to_file,
    base_executor.prints_with_substitution,
    base_executor.prints_banner_on_exit,
    base_executor.sends_installation_info
  )
  inherited_config = (
    mode_sync_executor.logs_to_file,
    mode_sync_executor.prints_with_substitution,
    mode_sync_executor.prints_banner_on_exit,
    mode_sync_executor.sends_installation_info
  )
  assert (
    inherited_config == base_config
  ), get_assertion_message("config values", base_config, inherited_config)

def test_sets_sync_program_variables_when_initializing():
  executor = DummySyncExecutor({})
  assert (
    (executor.sync_program_path, executor.sync_program_name) ==
    (__SYNC_PROGRAM_PATH, mode_sync_executor._SYNC_PROGRAM_NAME)
  ), get_assertion_message(
    "sync program variables",
    (executor.sync_program_path, executor.sync_program_name),
    (__SYNC_PROGRAM_PATH, mode_sync_executor._SYNC_PROGRAM_NAME)
  )

def test_calls_logger_when_sync_program_not_exists(
  __mock_os_path_exists,
  __mock_logger,
  __mock_logger_red
):
  __mock_os_path_exists.return_value = False
  DummySyncExecutor({}).run()
  error_message = __mock_logger_red(f"{__SYNC_PROGRAM_PATH} does not exist.")
  error_message += "\n"
  error_message += __mock_logger_red("Xmipp needs to be compiled successfully before running this command!")
  __mock_logger.assert_called_once_with(error_message)

def test_returns_error_when_sync_program_not_exists(
  __mock_os_path_exists
):
  __mock_os_path_exists.return_value = False
  executor = DummySyncExecutor({})
  ret_code, output = executor.run()
  assert (
    (ret_code, output) == (errors.IO_ERROR, "")
  ), get_assertion_message("return values", (errors.IO_ERROR, ""), (ret_code, output))

@pytest.mark.parametrize(
  "sync_output",
  [pytest.param((0, "success")), pytest.param((1, "failure"))]
)
def test_returns_execute_model_operation_result_when_sync_program_exists(
  __mock_os_path_exists,
  sync_output
):
  class ModifiableDummySyncExecutor(DummySyncExecutor):
    def _sync_operation(self):
      return sync_output
  __mock_os_path_exists.return_value = True
  ret_code, output = ModifiableDummySyncExecutor({}).run()
  assert (
    (ret_code, output) == sync_output
  ), get_assertion_message(
    "model operation output",
    sync_output,
    (ret_code, output)
  )

@pytest.fixture
def __dummy_test_mode_executor():
  class TestExecutor(mode_executor.ModeExecutor):
    def run(self):
      return 0, ""
  # For coverage
  TestExecutor({}).run()
  return TestExecutor

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
def __mock_os_path_exists():
  with patch("os.path.exists") as mock_method:
    yield mock_method
