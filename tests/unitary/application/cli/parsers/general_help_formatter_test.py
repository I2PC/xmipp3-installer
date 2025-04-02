from unittest.mock import patch

import pytest

from xmipp3_installer.application.cli.parsers.general_help_formatter import GeneralHelpFormatter
from xmipp3_installer.application.cli.arguments import modes, params

from ..... import get_assertion_message

___EPILOG_TEXT = """Example 1: ./xmipp
Example 2: ./xmipp compileAndInstall -j 4
"""
__NOTE_TEXT = f"""Note: You can also view a specific help message for each mode with \"./xmipp [mode] -h\".
Example: ./xmipp {modes.MODE_ALL} -h
"""
__PARAMS = {
  "param1": {
    params.SHORT_VERSION: "param1-short",
    params.LONG_VERSION: "param1-long"
  },
  "param2": {
    params.SHORT_VERSION: "param2-short"
  },
  "param3": {
    params.LONG_VERSION: "param3-long"
  },
  "param4": {}
}
__MODE_ARGS = {
  "mode1": ["param1", "param2"],
  "mode2": ["param3", "param1"],
  "mode3": ["param2"],
  "mode4": ["param4"],
  "mode5": [],
  "mode6": [["param1"], ["param2", "param3"]]
}
__MODES = {
  "section1": {
    "section1-mode1": {},
    "section1-mode2": {}
  },
  "section2": {
    "section2-mode1": {}
  }
}

def test_formats_help(
  __mock_modes,
  __mock_get_section_message,
  __mock_get_epilog,
  __mock_get_note,
  __mock_get_formatting_tabs,
  __setup_formatter
):
  formatted_help = __setup_formatter.format_help()
  expected_formatted_help = "Run Xmipp's installer script\n\nUsage: xmipp [options]\n"
  expected_formatted_help += __mock_get_section_message("section1")
  expected_formatted_help += __mock_get_section_message("section2")
  expected_formatted_help += f"\n{__mock_get_epilog()}"
  expected_formatted_help += __mock_get_note()
  expected_formatted_help = __mock_get_formatting_tabs(expected_formatted_help)
  assert (
    formatted_help == expected_formatted_help
  ), get_assertion_message("formatted help", expected_formatted_help, formatted_help)

def test_gets_expected_epilog(__setup_formatter):
  epilog = __setup_formatter._GeneralHelpFormatter__get_epilog()
  assert (
    epilog == ___EPILOG_TEXT
  ), get_assertion_message("epilog", ___EPILOG_TEXT, epilog)

def test_gets_expected_note(__setup_formatter, __mock_logger_yellow):
  note = __setup_formatter._GeneralHelpFormatter__get_note()
  expected_note = __mock_logger_yellow(__NOTE_TEXT)
  assert (
    note == expected_note
  ), get_assertion_message("note", expected_note, note)

def test_calls_logger_yellow_when_getting_note(__setup_formatter, __mock_logger_yellow):
  __setup_formatter._GeneralHelpFormatter__get_note()
  __mock_logger_yellow.assert_called_once_with(__NOTE_TEXT)

@pytest.mark.parametrize(
  "mode,expected_args_str",
  [
    pytest.param("mode1", "[param1-short] [param2-short]"),
    pytest.param("mode2", "[param3-long] [param1-short]"),
    pytest.param("mode3", "[param2-short]"),
    pytest.param("mode4", ""),
    pytest.param("mode5", ""),
    pytest.param("mode6", "([param1-short] | [param2-short] [param3-long])")
  ],
)
def test_gets_expected_mode_args_str(
  mode,
  expected_args_str,
  __mock_mode_args,
  __mock_params,
  __setup_formatter
):
  mode_args_str = __setup_formatter._GeneralHelpFormatter__get_mode_args_str(mode)
  assert (
    mode_args_str == expected_args_str
  ), get_assertion_message("arguments string", expected_args_str, mode_args_str)

def test_calls_text_with_limits_when_getting_mode_args_and_help_str(
  __mock_text_with_limits,
  __mock_get_mode_args_str,
  __mock_get_mode_help,
  __setup_formatter
):
  previous_text_message = "this is the previous text message"
  mode = "my_test_mode"
  __setup_formatter._GeneralHelpFormatter__get_mode_args_and_help_str(
    previous_text_message,
    mode
  )
  __mock_text_with_limits.assert_called_once_with(
    f"{previous_text_message}{__mock_get_mode_args_str(mode)}",
    __mock_get_mode_help(mode)
  )

@pytest.mark.parametrize(
  "section,expected_mode_args_and_help",
  [
    pytest.param("section1", "\tsection1-mode1 \tsection1-mode2 "),
    pytest.param("section2", "\tsection2-mode1 ")
  ],
)
def test_returns_expected_section_message(
  section,
  expected_mode_args_and_help,
  __mock_get_help_separator,
  __mock_modes,
  __mock_get_mode_args_and_help_str,
  __setup_formatter
):
  section_message = __setup_formatter._GeneralHelpFormatter__get_section_message(section)
  expected_section_message = f"{__mock_get_help_separator()}\t# {section} #\n\n{expected_mode_args_and_help}"
  assert (
    section_message == expected_section_message
  ), get_assertion_message("section message", expected_section_message, section_message)
  
@pytest.fixture
def __setup_formatter():
  return GeneralHelpFormatter("test")

@pytest.fixture
def __mock_logger_yellow():
  with patch(
    "xmipp3_installer.application.logger.logger.Logger.yellow"
  ) as mock_method:
    mock_method.side_effect = lambda text: f"format-start-{text}-format-end"
    yield mock_method

@pytest.fixture
def __mock_text_with_limits():
  with patch(
    "xmipp3_installer.application.cli.parsers.general_help_formatter.GeneralHelpFormatter._text_with_limits"
  ) as mock_method:
    yield mock_method

@pytest.fixture
def __mock_get_mode_help():
  with patch(
    "xmipp3_installer.application.cli.parsers.general_help_formatter.GeneralHelpFormatter._get_mode_help"
  ) as mock_method:
    mock_method.side_effect = lambda mode: f"this is mode {mode}'s help"
    yield mock_method

@pytest.fixture
def __mock_mode_args():
  with patch.object(modes, "MODE_ARGS", __MODE_ARGS):
    yield

@pytest.fixture
def __mock_params():
  with patch.object(params, "PARAMS", __PARAMS):
    yield

@pytest.fixture
def __mock_get_mode_args_str():
  with patch(
    "xmipp3_installer.application.cli.parsers.general_help_formatter.GeneralHelpFormatter._GeneralHelpFormatter__get_mode_args_str"
  ) as mock_method:
    mock_method.side_effect = lambda mode: f"[mode-{mode}-param1]"
    yield mock_method

@pytest.fixture
def __mock_get_help_separator():
  with patch(
    "xmipp3_installer.application.cli.parsers.general_help_formatter.GeneralHelpFormatter._get_help_separator"
  ) as mock_method:
    mock_method.return_value = '_____'
    yield mock_method

@pytest.fixture
def __mock_modes():
  with patch.object(modes, "MODES", __MODES):
    yield

@pytest.fixture
def __mock_get_mode_args_and_help_str():
  with patch(
    "xmipp3_installer.application.cli.parsers.general_help_formatter.GeneralHelpFormatter._GeneralHelpFormatter__get_mode_args_and_help_str"
  ) as mock_method:
    mock_method.side_effect = lambda mode_start, _: mode_start
    yield mock_method

@pytest.fixture
def __mock_get_section_message():
  with patch(
    "xmipp3_installer.application.cli.parsers.general_help_formatter.GeneralHelpFormatter._GeneralHelpFormatter__get_section_message"
  ) as mock_method:
    mock_method.side_effect = lambda section: f"section message for section {section}"
    yield mock_method

@pytest.fixture
def __mock_get_epilog():
  with patch(
    "xmipp3_installer.application.cli.parsers.general_help_formatter.GeneralHelpFormatter._GeneralHelpFormatter__get_epilog"
  ) as mock_method:
    mock_method.return_value = "This is the epilog message"
    yield mock_method

@pytest.fixture
def __mock_get_note():
  with patch(
    "xmipp3_installer.application.cli.parsers.general_help_formatter.GeneralHelpFormatter._GeneralHelpFormatter__get_note"
  ) as mock_method:
    mock_method.return_value = "This is the note message"
    yield mock_method

@pytest.fixture
def __mock_get_formatting_tabs():
  with patch(
    "xmipp3_installer.application.cli.parsers.format.get_formatting_tabs"
  ) as mock_method:
    mock_method.side_effect = lambda text: f"FORMAT START - {text} - FORMAT END"
    yield mock_method
