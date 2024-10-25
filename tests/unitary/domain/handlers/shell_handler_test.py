from unittest.mock import patch

import pytest

from xmipp3_installer.domain.handlers import shell_handler
from xmipp3_installer.application.logger.logger import logger

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
