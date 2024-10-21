from unittest.mock import patch

import pytest

from xmipp3_installer.application.cli.parsers.general_help_formatter import GeneralHelpFormatter
from xmipp3_installer.application.cli import arguments

from .... import get_assertion_message

___EPILOG_TEXT = """Example 1: ./xmipp
Example 2: ./xmipp compileAndInstall -j 4
"""
__NOTE_TEXT = f"""Note: You can also view a specific help message for each mode with \"./xmipp [mode] -h\".
Example: ./xmipp {arguments.MODE_ALL} -h
"""

"""
def test_formats_help(__setup_general_help_formatter):
  assert (
    __setup_general_help_formatter.format_help()
  ), "Received different formatted help than expected."
"""

def test_gets_expected_epilog(__setup_general_help_formatter):
  epilog = __setup_general_help_formatter._GeneralHelpFormatter__get_epilog()
  assertion_message = get_assertion_message("epilog", ___EPILOG_TEXT, epilog)
  assert (
    epilog == ___EPILOG_TEXT
  ), assertion_message

def test_gets_expected_note(__setup_general_help_formatter, __mock_logger_yellow):
  note = __setup_general_help_formatter._GeneralHelpFormatter__get_note()
  expected_note = __mock_logger_yellow(__NOTE_TEXT)
  assert (
    note == expected_note
  ), get_assertion_message("note", expected_note, note)

def test_calls_logger_yellow_with_expected_params(__setup_general_help_formatter, __mock_logger_yellow):
  __setup_general_help_formatter._GeneralHelpFormatter__get_note()
  __mock_logger_yellow.assert_called_once_with(__NOTE_TEXT)

@pytest.fixture
def __setup_general_help_formatter():
  yield GeneralHelpFormatter("test")

@pytest.fixture
def __mock_logger_yellow():
  with patch(
    "xmipp3_installer.application.logger.logger.Logger.yellow"
  ) as mock_method:
    def __return_with_afixes(text):
      return f"format-start-{text}-format-end"
    mock_method.side_effect = __return_with_afixes
    yield mock_method
