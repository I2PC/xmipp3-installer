from unittest.mock import patch, MagicMock

import pytest

from xmipp3_installer.installer import installer_service
from xmipp3_installer.application.cli.arguments import modes
from xmipp3_installer.installer.installer_service import mode_selector

from ... import get_assertion_message

__MODE_NAME = "mode1"
__SELECTED_MODE_MESASGE = "selected mode"
__MODE_ALL_MESSAGE = "mode all"

@pytest.mark.parametrize(
  "args,expected_executor_key",
  [
    pytest.param({}, modes.MODE_ALL),
    pytest.param({modes.MODE: modes.MODE_ALL}, modes.MODE_ALL),
    pytest.param({modes.MODE: __MODE_NAME}, __MODE_NAME)
  ]
)
def test_calls_expected_executor_run_when_running_installer(
  args,
  expected_executor_key,
  mock_mode_executors,
  mock_sys_exit
):
  installer_service.run_installer(args)
  expected_executor = mock_mode_executors[expected_executor_key](args)
  expected_executor.run.assert_called_once_with()

@pytest.mark.parametrize(
  "args,other_executor_key",
  [
    pytest.param({}, __MODE_NAME),
    pytest.param({modes.MODE: modes.MODE_ALL}, __MODE_NAME),
    pytest.param({modes.MODE: __MODE_NAME}, modes.MODE_ALL)
  ]
)
def test_does_not_call_other_executor_run_when_running_installer(
  args,
  other_executor_key,
  mock_mode_executors,
  mock_sys_exit
):
  installer_service.run_installer(args)
  expected_executor = mock_mode_executors[other_executor_key](args)
  expected_executor.run.assert_not_called()

@pytest.mark.parametrize("mock_mode_executors", [pytest.param((0, 1))], indirect=["mock_mode_executors"])
def test_calls_logger_log_error_with_non_zero_ret_code_when_running_installer(
  mock_mode_executors,
  mock_logger_log_error,
  mock_sys_exit
):
  installer_service.run_installer({})
  executor = mock_mode_executors[modes.MODE_ALL]({})
  ret_code, output = executor.run.return_value
  mock_logger_log_error.assert_called_once_with(output, ret_code=ret_code)

@pytest.mark.parametrize(
  "mock_mode_executors",
  [
    pytest.param((0, 0)),
    pytest.param((0, 1))
  ],
  indirect=["mock_mode_executors"]
)
def test_exits_with_run_return_code(mock_mode_executors, mock_logger_log_error):
  executor = mock_mode_executors[modes.MODE_ALL]({})
  ret_code, _ = executor.run.return_value
  with pytest.raises(SystemExit) as pytest_exit:
    installer_service.run_installer({})
  assert (
    ret_code == pytest_exit.value.code
  ), get_assertion_message("return code", ret_code, pytest_exit.value.code)

def __mock_executor(ret_code, message):
  executor = MagicMock()
  executor.run.return_value = (ret_code, message)
  return executor

@pytest.fixture(params=[(0, 0)])
def mock_mode_executors(request):
  selected_executor = __mock_executor(request.param[0], __SELECTED_MODE_MESASGE)
  all_executor = __mock_executor(request.param[1], __MODE_ALL_MESSAGE)
  with patch.object(mode_selector, 'MODE_EXECUTORS', {
    __MODE_NAME: lambda _: selected_executor,
    modes.MODE_ALL: lambda _: all_executor
  }) as mock_object:
    yield mock_object

@pytest.fixture
def mock_logger_log_error():
  with patch(
    'xmipp3_installer.application.logger.logger.Logger.log_error'
  ) as mock_method:
    yield mock_method

@pytest.fixture
def mock_sys_exit():
  with patch("sys.exit") as mock_method:
    yield mock_method
