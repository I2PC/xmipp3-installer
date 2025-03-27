from subprocess import PIPE
from unittest.mock import patch, Mock, call

import pytest

from xmipp3_installer.installer.handlers import shell_handler
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.application.logger import errors

from .... import get_assertion_message

__COMMAND = "echo Hi"
__RET_CODE_TEXT = "return code"

def test_calls_logger_to_show_command_when_running_shell_command(
  __mock_logger,
  __mock_run_command
):
  shell_handler.run_shell_command(
    __COMMAND,
    show_command=True
  )
  __mock_logger.assert_called_once_with(
    logger.blue(__COMMAND)
  )

def test_calls_logger_to_show_output_when_running_shell_command(
  __mock_logger,
  __mock_run_command
):
  shell_handler.run_shell_command(
    __COMMAND,
    show_output=True
  )
  __mock_logger.assert_called_once_with(
    __mock_run_command()[1]
  )

@pytest.mark.parametrize("ret_code", [pytest.param(1), pytest.param(2)])
def test_calls_logger_to_show_error_when_running_shell_command(
  ret_code,
  __mock_logger_error,
  __mock_run_command
):
  __mock_run_command.return_value = (ret_code, 'test_error_message')
  shell_handler.run_shell_command(
    __COMMAND,
    show_error=True
  )
  __mock_logger_error.assert_called_once_with(
    __mock_run_command()[1],
    ret_code=ret_code
  )

def test_returns_interrupted_error_if_receives_keyboard_interrupt_when_running_command(
  __mock_process_wait_keyboard_interrupt
):
  ret_code = shell_handler.__run_command(__COMMAND)[0]
  assert (
    ret_code == errors.INTERRUPTED_ERROR
  ), get_assertion_message(__RET_CODE_TEXT, errors.INTERRUPTED_ERROR, ret_code)

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
  __mock_process_communicate().returncode = ret_code
  return_values = shell_handler.__run_command(__COMMAND)
  assert (
    return_values == (ret_code, expected_message)
  ), get_assertion_message("return values", (ret_code, expected_message), return_values)

@pytest.mark.parametrize(
  "substitute",
  [pytest.param(False), pytest.param(True)]
)
def test_calls_logger_when_running_shell_command_in_streaming(
  substitute,
  __mock_popen,
  __mock_thread,
  __mock_logger,
  __mock_log_in_streaming
):
  shell_handler.run_shell_command_in_streaming(__COMMAND, substitute=substitute)
  __mock_logger.assert_called_once_with(__COMMAND, substitute=substitute)

def test_calls_popen_when_running_shell_command_in_streaming(
  __mock_popen,
  __mock_thread,
  __mock_logger,
  __mock_log_in_streaming
):
  shell_handler.run_shell_command_in_streaming(__COMMAND)
  __mock_popen.assert_called_with(__COMMAND, cwd='./', stdout=PIPE, stderr=PIPE, shell=True)

@pytest.mark.parametrize(
  "show_output,show_error,substitute",
  [
    pytest.param(False, False, False),
    pytest.param(False, False, True),
    pytest.param(False, True, False),
    pytest.param(False, True, True),
    pytest.param(True, False, False),
    pytest.param(True, False, True),
    pytest.param(True, True, False),
    pytest.param(True, True, True)
  ]
)
def test_calls_thread_when_running_shell_command_in_streaming(
  show_output,
  show_error,
  substitute,
  __mock_popen,
  __mock_thread,
  __mock_logger,
  __mock_log_in_streaming
):
  shell_handler.run_shell_command_in_streaming(
    __COMMAND,
    show_output=show_output,
    show_error=show_error,
    substitute=substitute
  )
  mock_stdout = __mock_popen().stdout
  mock_stderr = __mock_popen().stderr
  __mock_thread.assert_has_calls([
    call(
      target=__mock_log_in_streaming,
      args=(mock_stdout,),
      kwargs={"show_in_terminal": show_output, "substitute": substitute, "err": False}
    ),
    call(
      target=__mock_log_in_streaming,
      args=(mock_stderr,),
      kwargs={"show_in_terminal": show_error, "substitute": substitute, "err": True}
    )
  ])

def test_calls_process_wait_when_running_shell_command_in_streaming(
  __mock_popen,
  __mock_thread,
  __mock_logger,
  __mock_log_in_streaming
):
  shell_handler.run_shell_command_in_streaming(__COMMAND)
  __mock_popen().wait.assert_called_once_with()

def test_returns_interrupted_error_when__keyboard_interrupt_while_running_shell_command_in_streaming(
  __mock_process_wait_keyboard_interrupt,
  __mock_thread,
  __mock_logger,
  __mock_log_in_streaming
):
  ret_code = shell_handler.run_shell_command_in_streaming(__COMMAND)
  assert (
    ret_code == errors.INTERRUPTED_ERROR
  ), get_assertion_message(__RET_CODE_TEXT, errors.INTERRUPTED_ERROR, ret_code)

@pytest.mark.parametrize("expected_ret_code", [pytest.param(0), pytest.param(1)])
def test_returns_expected_ret_code_when_running_shell_command_in_streaming(
  expected_ret_code,
  __mock_popen,
  __mock_thread,
  __mock_logger,
  __mock_log_in_streaming
):
  __mock_popen().returncode = expected_ret_code
  ret_code = shell_handler.run_shell_command_in_streaming(__COMMAND)
  assert (
    ret_code == expected_ret_code
  ), get_assertion_message(__RET_CODE_TEXT, expected_ret_code, ret_code)

@pytest.fixture
def __mock_run_command():
  with patch(
    "xmipp3_installer.installer.handlers.shell_handler.__run_command"
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
def __mock_stdout():
  mock_stdout = Mock()
  mock_stdout.read.return_value = b"Hi\n"
  return mock_stdout

@pytest.fixture
def __mock_stderr():
  mock_stderr = Mock()
  mock_stderr.read.return_value =b"Error\n"
  return mock_stderr

@pytest.fixture
def __mock_popen(__mock_stdout, __mock_stderr):
  with patch("subprocess.Popen") as mock_method:
    mock_process = Mock()
    mock_process.stdout = __mock_stdout()
    mock_process.stderr = __mock_stderr()
    mock_process.wait.return_value = None

    mock_method.return_value = mock_process
    yield mock_method

@pytest.fixture
def __mock_process_wait_keyboard_interrupt(__mock_popen):
  __mock_popen().wait.side_effect = KeyboardInterrupt
  yield __mock_popen

@pytest.fixture(params=[('defaulf_output', 'default_err')])
def __mock_process_communicate(request, __mock_popen):
  raw_messages = request.param
  messages = (raw_messages[0].encode(), raw_messages[1].encode())
  __mock_popen().communicate.return_value = messages
  yield __mock_popen

@pytest.fixture
def __mock_log_in_streaming():
  with patch(
    "xmipp3_installer.application.logger.logger.Logger.log_in_streaming"
  ) as mock_method:
    yield mock_method

@pytest.fixture
def __mock_thread():
  with patch("threading.Thread") as mock_method:
    mock_thread = Mock()
    mock_thread.start.return_value = None
    mock_thread.join.return_value = None

    mock_method.return_value = mock_thread
    yield mock_method
