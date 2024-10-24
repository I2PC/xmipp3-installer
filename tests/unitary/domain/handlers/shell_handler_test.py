from unittest.mock import patch

import pytest

from xmipp3_installer.domain.handlers import shell_handler
from xmipp3_installer.application.logger.logger import logger

__COMMAND = "echo Hi"

def test_calls_logger_to_show_command_when_running_shell_command(
  __mock_logger,
  __mock_run_command
):
  shell_handler.run_shell_command(__COMMAND, show_command=True)
  __mock_logger.assert_called_once_with(
    logger.blue(__COMMAND),
    substitute=False
  )

@pytest.fixture
def __mock_run_command():
  with patch(
    "xmipp3_installer.domain.handlers.shell_handler.__run_command"
  ) as mock_method:
    mock_method.return_value = (0, '')
    yield mock_method

@pytest.fixture
def __mock_logger():
  with patch(
    "xmipp3_installer.application.logger.logger.Logger.__call__"
  ) as mock_method:
    yield mock_method
