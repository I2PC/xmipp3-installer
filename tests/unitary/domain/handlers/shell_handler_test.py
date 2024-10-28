from subprocess import PIPE
from unittest.mock import patch, MagicMock

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

def test_run_shell_command_in_streaming(
  __mock_popen,
  __mock_stdout,
  __mock_thread,
  __mock_logger,
  __mock_log_in_streaming
):
  # Call the function
  shell_handler.run_shell_command_in_streaming(__COMMAND, show_output=True, show_error=True)

  # Check if Popen was called correctly
  __mock_popen.assert_called_with(__COMMAND, cwd='./', stdout=PIPE, stderr=PIPE, shell=True)

  # Check if threads were created and started
  assert __mock_thread.call_count == 2
  __mock_thread.assert_any_call(target=logger.log_in_streaming, args=(__mock_stdout,), kwargs={"show_in_terminal": True, "substitute": False, "err": False})
  __mock_thread.assert_any_call(target=logger.log_in_streaming, args=(mock_stderr,), kwargs={"show_in_terminal": True, "substitute": False, "err": True})

  # Check if process.wait() was called
  mock_process.wait.assert_called_once()

  # Simulate process.wait() raising KeyboardInterrupt
  mock_process.wait.side_effect = KeyboardInterrupt
  ret_code = shell_handler.run_shell_command_in_streaming(__COMMAND, show_output=True, show_error=True)
  assert ret_code 

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

@pytest.fixture
def __mock_log_in_streaming():
  with patch(
    "xmipp3_installer.application.logger.logger.Logger.log_in_streaming"
  ) as mock_method:
    yield mock_method

@pytest.fixture
def __mock_popen():
  with patch("subprocess.Popen") as mock_method:
    mock_stdout = MagicMock()
    mock_stderr = MagicMock()
    mock_stdout.read.return_value = b"Hi\n"
    mock_stderr.read.return_value = b"Error\n"

    mock_process = MagicMock()
    mock_process.stdout = mock_stdout
    mock_process.stderr = mock_stderr

    mock_method.return_value = mock_process
    yield mock_method

@pytest.fixture
def __mock_thread():
  with patch("threading.Popen") as mock_method:
    yield mock_method

@pytest.fixture
def __mock_stdout():
  mock_stdout = MagicMock()
  mock_stdout.read.return_value = b"Hi\n"
  return mock_stdout
