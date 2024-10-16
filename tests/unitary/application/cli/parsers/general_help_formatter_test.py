from unittest.mock import patch

import pytest

from xmipp3_installer.application.cli.parsers.general_help_formatter import GeneralHelpFormatter
from xmipp3_installer.application.cli import arguments

from .... import get_assertion_message

___EPILOG_TEXT = """Example 1: ./xmipp
Example 2: ./xmipp compileAndInstall -j 4
"""
__NOTE_TEXT = f"""Note: You can also view a specific help message for each mode with \"./xmipp [mode] -h\".
"Example: ./xmipp {arguments.MODE_ALL} -h
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


"""
def test_gets_expected_note(__setup_general_help_formatter):
  note = __setup_general_help_formatter._GeneralHelpFormatter__get_note()
  assert (
    note == __NOTE_TEXT
  ), get_assertion_message("note", __NOTE_TEXT, note)
"""

@pytest.fixture
def __setup_general_help_formatter():
  yield GeneralHelpFormatter("test")
