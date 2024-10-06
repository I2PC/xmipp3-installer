from unittest.mock import patch

import pytest

from xmipp3_installer.application.cli import cli
from xmipp3_installer.application.cli import arguments

def test_calls_add_default_usage_mode(__mock_sys_argv, __mock_add_default_usage_mode):
  cli.main()
  __mock_add_default_usage_mode.assert_called_once()


@pytest.fixture
def __mock_sys_argv():
  with patch(
    "sys.argv"
  ) as mock_method:
    mock_method.return_value = [arguments.XMIPP_PROGRAM_NAME, "-h"]
    yield mock_method

@pytest.fixture
def __mock_add_default_usage_mode():
  with patch(
    "xmipp3_installer.application.cli.cli.__add_default_usage_mode"
  ) as mock_method:
    yield mock_method

@pytest.fixture
def __mock_parse_args():
  with patch(
    "argparse.ArgumentParser.parse_args"
  ) as mock_method:
    yield mock_method
