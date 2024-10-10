from unittest.mock import patch

import pytest

from xmipp3_installer.application.cli.parsers.base_help_formatter import BaseHelpFormatter
from xmipp3_installer.application.cli import arguments

__MODES = {
  "group1": {
    "mode1": ["mode1-message1", "mode1-message2"],
    "mode2": ["mode2-message1", "mode2-message2", "mode2-message3"]
  },
  "group2": {
    "mode3": ["mode3-message1"]
  }
}

@pytest.mark.parametrize(
  "mode,general,expected_help_message",
  [
    pytest.param("mode1", True, "mode1-message1"),
    pytest.param("mode1", False, "mode1-message1\nmode1-message2"),
    pytest.param("mode2", True, "mode2-message1"),
    pytest.param("mode3", True, "mode3-message1"),
    pytest.param("mode3", False, "mode3-message1")
  ],
)
def test_returns_expected_help_message(
  mode,
  general,
  expected_help_message,
  __setup_parser,
  __mock_modes
):
  assert (
    __setup_parser._get_mode_help(mode, general=general) == expected_help_message
  ), "Received different help message than expected."

@pytest.fixture
def __setup_parser():
  yield BaseHelpFormatter("test")

@pytest.fixture
def __mock_modes():
  with patch.object(arguments, "MODES", __MODES):
    yield
