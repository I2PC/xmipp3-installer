from unittest.mock import patch

import pytest

from xmipp3_installer.domain.handlers import shell_handler
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.application.logger import errors

from .... import get_assertion_message

__COMMAND = "echo Hi"

@pytest.mark.parametrize(
  "substitute",
  [
    pytest.param(False),
    pytest.param(True)
  ]
)
def test_calls_logger_to_show_command_when_running_shell_command(
  substitute,
  __mock_logger,
  __mock_run_command
):
  shell_handler.run_shell_command(
    __COMMAND,
    show_command=True,
    substitute=substitute
  )
  __mock_logger.assert_called_once_with(
    logger.blue(__COMMAND),
    substitute=substitute
  )

@pytest.mark.parametrize(
  "substitute",
  [
    pytest.param(False),
    pytest.param(True)
  ]
)
def test_calls_logger_to_show_output_when_running_shell_command(
  substitute,
  __mock_logger,
  __mock_run_command
):
  shell_handler.run_shell_command(
    __COMMAND,
    show_output=True,
    substitute=substitute
  )
  __mock_logger.assert_called_once_with(
    __mock_run_command()[1],
    substitute=substitute
  )

@pytest.mark.parametrize(
  "substitute,ret_code",
  [
    pytest.param(False, 1),
    pytest.param(True, 2)
  ]
)
def test_calls_logger_to_show_error_when_running_shell_command(
  substitute,
  ret_code,
  __mock_logger_error,
  __mock_run_command
):
  __mock_run_command.return_value = (ret_code, 'test_error_message')
  shell_handler.run_shell_command(
    __COMMAND,
    show_error=True,
    substitute=substitute
  )
  __mock_logger_error.assert_called_once_with(
    __mock_run_command()[1],
    ret_code=ret_code,
    substitute=substitute
  )

def test_returns_interrupted_error_if_receives_keyboard_interrupt_when_running_command(
  __mock_process_wait
):
  ret_code = shell_handler.__run_command(__COMMAND)[0]
  assert (
    ret_code == errors.INTERRUPTED_ERROR
  ), get_assertion_message("return code", errors.INTERRUPTED_ERROR, ret_code)

@pytest.mark.parametrize(
  "ret_code,__mock_process_communicate,expected_message",
  [
    pytest.param(0, ("test_output", "test_error"), "test_output"),
    pytest.param(1, ("test_output", "test_error"), "test_error")
  ],
  indirect=["__mock_process_communicate"]
)
def test_returns_expected_ret_code_and_message_when_running_command(
  ret_code,
  __mock_process_communicate,
  expected_message
):
  command = __COMMAND if ret_code == 0 else "this_command_will_not_work"
  return_values = shell_handler.__run_command(command)
  return_values = (1, return_values[1]) if return_values[0] != 0 else return_values
  assert (
    return_values == (ret_code, expected_message)
  ), get_assertion_message("return values", (ret_code, expected_message), return_values)

@pytest.fixture
def __mock_run_command():
  with patch(
    "xmipp3_installer.domain.handlers.shell_handler.__run_command"
  ) as mock_method:
    mock_method.return_value = (0, 'test_output')
    yield mock_method

@pytest.fixture
def __mock_logger():
  with patch(
    "xmipp3_installer.application.logger.logger.Logger.__call__"
  ) as mock_method:
    yield mock_method

@pytest.fixture
def __mock_logger_error():
  with patch(
    "xmipp3_installer.application.logger.logger.Logger.log_error"
  ) as mock_method:
    yield mock_method

@pytest.fixture
def __mock_process_wait():
  def __raise_keyboard_interrupt():
    raise KeyboardInterrupt
  with patch("subprocess.Popen.wait") as mock_method:
    mock_method.side_effect = __raise_keyboard_interrupt
    yield mock_method

@pytest.fixture
def __mock_process_communicate(request):
  raw_messages = request.param if hasattr(request, "param") else ('defaulf_output', 'default_err')
  messages = (raw_messages[0].encode(), raw_messages[1].encode())
  with patch("subprocess.Popen.communicate") as mock_method:
    mock_method.return_value = messages
    yield mock_method
