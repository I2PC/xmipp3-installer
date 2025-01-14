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
  __mock_mode_executors,
  __mock_sys_exit
):
  installer_service.run_installer(args)
  expected_executor = __mock_mode_executors[expected_executor_key](args)
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
  __mock_mode_executors,
  __mock_sys_exit
):
  installer_service.run_installer(args)
  expected_executor = __mock_mode_executors[other_executor_key](args)
  expected_executor.run.assert_not_called()

@pytest.mark.parametrize("__mock_mode_executors", [pytest.param((0, 1))], indirect=["__mock_mode_executors"])
def test_calls_logger_log_error_when_running_installer_with_non_zero_ret_code(
  __mock_mode_executors,
  __mock_logger_log_error,
  __mock_sys_exit
):
  installer_service.run_installer({})
  executor = __mock_mode_executors[modes.MODE_ALL]({})
  ret_code, output = executor.run()
  __mock_logger_log_error.assert_called_once_with(output, ret_code=ret_code)

@pytest.mark.parametrize(
  "__mock_mode_executors_prints_on_exit,expected_call_count",
  [
    pytest.param(False, 0),
    pytest.param(True, 1)
  ],
  indirect=["__mock_mode_executors_prints_on_exit"]
)
def test_calls_get_success_message_when_running_executor_with_zero_exit_code_deppending_on_attribute(
  __mock_mode_executors_prints_on_exit,
  expected_call_count,
  __mock_get_success_message,
  __mock_logger,
  __mock_sys_exit
):
  installer_service.run_installer({})
  assert (
    __mock_get_success_message.call_count == expected_call_count
  ), get_assertion_message(
    "get success message call count",
    expected_call_count,
    __mock_get_success_message.call_count
  )

@pytest.mark.parametrize(
  "__mock_mode_executors",
  [
    pytest.param((0, 0)),
    pytest.param((0, 1))
  ],
  indirect=["__mock_mode_executors"]
)
def test_exits_with_run_return_code(
  __mock_mode_executors,
  __mock_logger_log_error,
  __mock_get_success_message,
  __mock_logger
):
  executor = __mock_mode_executors[modes.MODE_ALL]({})
  ret_code, _ = executor.run.return_value
  with pytest.raises(SystemExit) as pytest_exit:
    installer_service.run_installer({})
  assert (
    ret_code == pytest_exit.value.code
  ), get_assertion_message("return code", ret_code, pytest_exit.value.code)

def __mock_executor(ret_code, message):
  executor = MagicMock()
  executor.run.return_value = (ret_code, message)
  executor.prints_banner_on_exit = False
  return executor

@pytest.fixture(params=[(0, 0)])
def __mock_mode_executors(request):
  selected_executor = __mock_executor(request.param[0], __SELECTED_MODE_MESASGE)
  all_executor = __mock_executor(request.param[1], __MODE_ALL_MESSAGE)
  with patch.object(mode_selector, 'MODE_EXECUTORS', {
    __MODE_NAME: lambda _: selected_executor,
    modes.MODE_ALL: lambda _: all_executor
  }) as mock_object:
    yield mock_object

@pytest.fixture(params=[False])
def __mock_mode_executors_prints_on_exit(__mock_mode_executors, request):
  all_executor = __mock_executor(0, __MODE_ALL_MESSAGE)
  all_executor.prints_banner_on_exit = request.param
  __mock_mode_executors['all'] = lambda _: all_executor
  yield __mock_mode_executors

@pytest.fixture
def __mock_logger_log_error():
  with patch(
    'xmipp3_installer.application.logger.logger.Logger.log_error'
  ) as mock_method:
    yield mock_method

@pytest.fixture
def __mock_sys_exit():
  with patch("sys.exit") as mock_method:
    yield mock_method

@pytest.fixture
def __mock_get_success_message():
  with patch(
    "xmipp3_installer.application.logger.predefined_messages.get_success_message"
  ) as mock_method:
    mock_method.return_value = "success message"
    yield mock_method

@pytest.fixture
def __mock_logger():
	with patch(
		"xmipp3_installer.application.logger.logger.Logger.__call__"
	) as mock_method:
		yield mock_method
