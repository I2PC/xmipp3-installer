from io import BytesIO
from unittest.mock import patch, Mock, call, MagicMock

import pytest

from xmipp3_installer.shared.singleton import Singleton
from xmipp3_installer.application.logger.logger import Logger
from xmipp3_installer.application.logger import errors
from xmipp3_installer.installer import urls

from .... import get_assertion_message, MockTerminalSize

__SAMPLE_TEXT = "this is some sample text"
__ERROR_MESSAGE = "Test error message"
__ERROR_CODES = {
  1: ['Error 1 first', 'error 1 second'],
  2: ['Error 2 first', ''],
  3: ['', ''],
  4: ['', 'Error 4 second']
}
__PORTAL_LINK_MESSAGE = f"\nMore details on the Xmipp documentation portal: {urls.DOCUMENTATION_URL}"
__DUMMY_FILE = BytesIO()
__STREAM_READLINE = [b'line1\n', b'line2\n', b'']
__STREAM_READLINE_DECODED = ['line1', 'line2']

def test_inherits_from_singleton_class():
  logger = Logger()
  assert isinstance(logger, Singleton)

def test_formats_green(
  __mock_color_green,
  __mock_reset_format
):
  logger = Logger()
  formatted_text = logger.green(__SAMPLE_TEXT)
  expected_formatted_text = f"{__mock_color_green}{__SAMPLE_TEXT}{__mock_reset_format}"
  assert (
    formatted_text == expected_formatted_text
  ), get_assertion_message("green format", expected_formatted_text, formatted_text)

def test_formats_yellow(
  __mock_color_yellow,
  __mock_reset_format
):
  logger = Logger()
  formatted_text = logger.yellow(__SAMPLE_TEXT)
  expected_formatted_text = f"{__mock_color_yellow}{__SAMPLE_TEXT}{__mock_reset_format}"
  assert (
    formatted_text == expected_formatted_text
  ), get_assertion_message("yellow format", expected_formatted_text, formatted_text)

def test_formats_red(
  __mock_color_red,
  __mock_reset_format
):
  logger = Logger()
  formatted_text = logger.red(__SAMPLE_TEXT)
  expected_formatted_text = f"{__mock_color_red}{__SAMPLE_TEXT}{__mock_reset_format}"
  assert (
    formatted_text == expected_formatted_text
  ), get_assertion_message("red format", expected_formatted_text, formatted_text)

def test_formats_blue(
  __mock_color_blue,
  __mock_reset_format
):
  logger = Logger()
  formatted_text = logger.blue(__SAMPLE_TEXT)
  expected_formatted_text = f"{__mock_color_blue}{__SAMPLE_TEXT}{__mock_reset_format}"
  assert (
    formatted_text == expected_formatted_text
  ), get_assertion_message("blue format", expected_formatted_text, formatted_text)

def test_formats_bold(
  __mock_bold,
  __mock_reset_format
):
  logger = Logger()
  formatted_text = logger.bold(__SAMPLE_TEXT)
  expected_formatted_text = f"{__mock_bold}{__SAMPLE_TEXT}{__mock_reset_format}"
  assert (
    formatted_text == expected_formatted_text
  ), get_assertion_message("bold format", expected_formatted_text, formatted_text)

def test_calls_open_when_starting_log_file_and_log_file_is_not_open(
  __mock_open
):
  log_file_name = "test_log_file"
  logger = Logger()
  logger.start_log_file(log_file_name)
  __mock_open.assert_called_once_with(log_file_name, 'w', encoding="utf-8")

def test_does_not_call_open_when_starting_log_file_and_log_file_is_open(
  __mock_open
):
  log_file_name = "test_log_file"
  logger = Logger()
  logger._Logger__log_file = "Something not None"
  logger.start_log_file(log_file_name)
  __mock_open.assert_not_called()

def test_starts_log_file(__mock_open):
  logger = Logger()
  logger.start_log_file("test_log_file")
  log_file = logger._Logger__log_file
  assert (
    log_file is __DUMMY_FILE
  ), get_assertion_message("log file", __DUMMY_FILE, log_file)

def test_sets_file_to_none_after_closing():
  mock_file = MagicMock()
  logger = Logger()
  logger._Logger__log_file = mock_file
  logger.close()
  assert (
    logger._Logger__log_file is None
  ), get_assertion_message("logger file", None, logger._Logger__log_file)

def test_calls_close_on_open_log_file_if_it_has_been_set():
  mock_file = MagicMock()
  logger = Logger()
  logger._Logger__log_file = mock_file
  logger.close()
  mock_file.close.assert_called_once_with()

def test_does_not_call_close_on_open_log_file_if_it_has_not_been_set():
  mock_file = MagicMock()
  logger = Logger()
  logger.close()
  mock_file.close.assert_not_called()

@pytest.mark.parametrize(
  "expected_allow_substitution",
  [
    pytest.param(False),
    pytest.param(True)
  ],
)
def test_sets_allow_substitution(expected_allow_substitution):
  logger = Logger()
  logger.set_allow_substitution(expected_allow_substitution)
  allow_substitution = logger._Logger__allow_substitution
  assert (
    allow_substitution == expected_allow_substitution
  ), get_assertion_message("allow substitution value", expected_allow_substitution, allow_substitution)

@pytest.mark.parametrize(
  "error_message,ret_code,add_link,add_link_message,first_expected_message,second_expected_message",
  [
    pytest.param("", 1, False, '', __ERROR_CODES[1][0], f"\n{__ERROR_CODES[1][1]}"),
    pytest.param(__ERROR_MESSAGE, 1, False, '', __ERROR_CODES[1][0], f"\n{__ERROR_CODES[1][1]}"),
    pytest.param("", 1, True, __PORTAL_LINK_MESSAGE,  __ERROR_CODES[1][0], f"\n{__ERROR_CODES[1][1]}"),
    pytest.param(__ERROR_MESSAGE, 1, True, __PORTAL_LINK_MESSAGE,  __ERROR_CODES[1][0], f"\n{__ERROR_CODES[1][1]}"),
    pytest.param("", 2, False, '',  __ERROR_CODES[2][0], ''),
    pytest.param(__ERROR_MESSAGE, 2, False, '',  __ERROR_CODES[2][0], ''),
    pytest.param("", 2, True, __PORTAL_LINK_MESSAGE, __ERROR_CODES[2][0], ''),
    pytest.param(__ERROR_MESSAGE, 2, True, __PORTAL_LINK_MESSAGE, __ERROR_CODES[2][0], ''),
    pytest.param("", 3, False, '', '', ''),
    pytest.param(__ERROR_MESSAGE, 3, False, '', '', ''),
    pytest.param("", 3, True, __PORTAL_LINK_MESSAGE, '', ''),
    pytest.param(__ERROR_MESSAGE, 3, True, __PORTAL_LINK_MESSAGE, '', ''),
    pytest.param("", 4, False, '', '', f"\n{__ERROR_CODES[4][1]}"),
    pytest.param(__ERROR_MESSAGE, 4, False, '', '', f"\n{__ERROR_CODES[4][1]}"),
    pytest.param("", 4, True, __PORTAL_LINK_MESSAGE, '', f"\n{__ERROR_CODES[4][1]}"),
    pytest.param(__ERROR_MESSAGE, 4, True, __PORTAL_LINK_MESSAGE, '', f"\n{__ERROR_CODES[4][1]}"),
    pytest.param("", 'no-existe', False, '', __ERROR_CODES[1][0], f"\n{__ERROR_CODES[1][1]}"),
    pytest.param(__ERROR_MESSAGE, 'no-existe', False, '', __ERROR_CODES[1][0], f"\n{__ERROR_CODES[1][1]}"),
    pytest.param("", 'no-existe', True, __PORTAL_LINK_MESSAGE, __ERROR_CODES[1][0], f"\n{__ERROR_CODES[1][1]}"),
    pytest.param(__ERROR_MESSAGE, 'no-existe', True, __PORTAL_LINK_MESSAGE, __ERROR_CODES[1][0], f"\n{__ERROR_CODES[1][1]}")
  ],
)
def test_calls_logger_with_expected_params_when_logging_error(
  error_message,
  ret_code,
  add_link,
  add_link_message,
  first_expected_message,
  second_expected_message,
  __mock_call,
  __mock_color_red,
  __mock_reset_format,
  __mock_errors
):
  logger = Logger()
  logger.log_error(error_message, ret_code=ret_code, add_portal_link=add_link)
  __mock_call.assert_called_once_with(
    logger.red(''.join([
      f"{error_message}\n\n" if error_message else '',
      f"Error {ret_code}: {first_expected_message}",
      second_expected_message,
      add_link_message
    ])),
    show_in_terminal=True
  )

def test_returns_expected_text_when_removing_non_printable_characters():
  printable_text = "This text should remain"
  logger = Logger()
  modified_text = logger._Logger__remove_non_printable(
    logger.blue(logger.yellow(logger.red(logger.bold(logger.green(printable_text)))))
  )
  assert (
    modified_text == printable_text
  ), get_assertion_message("text without printable characters", printable_text, modified_text)

@pytest.mark.parametrize(
  "__mock_get_terminal_column_size,last_printed_element,expected_n_last_lines",
  [
    pytest.param(10, None, 0),
    pytest.param(0, None, 0),
    pytest.param(2, "a", 1),
    pytest.param(2, "aaa", 2),
    pytest.param(2, "aa", 1),
    pytest.param(5, "a\n", 2),
    pytest.param(3, "a\naaaa", 3),
    pytest.param(3, "aaaa\naaaa", 4),
    pytest.param(3, "", 1),
    pytest.param(3, "\n", 2)
  ],
  indirect=["__mock_get_terminal_column_size"]
)
def test_returns_expected_n_last_lines(
  __mock_get_terminal_column_size,
  last_printed_element,
  expected_n_last_lines
):
  logger = Logger()
  with patch.object(logger, "_Logger__last_printed_elem", last_printed_element):
    n_last_lines = logger._Logger__get_n_last_lines()
  assert (
    n_last_lines == expected_n_last_lines
  ), get_assertion_message("number of lines from last print", expected_n_last_lines, n_last_lines)

@pytest.mark.parametrize(
  "__mock_get_n_last_lines",
  [
    pytest.param(1),
    pytest.param(2),
    pytest.param(0)
  ],
  indirect=["__mock_get_n_last_lines"]
)
def test_returns_the_expected_text_when_substituting_lines(
  __mock_get_n_last_lines,
  __mock_up,
  __mock_remove_line
):
  sample_text = "This is some sample text"
  logger = Logger()
  substituted_text = logger._Logger__substitute_lines(sample_text)
  expected_substituted_text = f"{__get_substitution_chars(__mock_up, __mock_remove_line, __mock_get_n_last_lines())}{sample_text}"
  assert (
    substituted_text == expected_substituted_text
  ), get_assertion_message("text with substitution characters", expected_substituted_text, substituted_text)

@pytest.mark.parametrize(
  "show_in_terminal,substitute",
  [
    pytest.param(True, False),
    pytest.param(True, True)
  ],
)
def test_calls_print_when_calling_logger_without_file_and_with_substitution(
  show_in_terminal,
  substitute,
  __mock_substitute_lines,
  __mock_print
):
  logger = Logger()
  logger(__SAMPLE_TEXT, show_in_terminal=show_in_terminal, substitute=substitute)
  expected_text = __mock_substitute_lines(__SAMPLE_TEXT) if substitute else __SAMPLE_TEXT
  __mock_print.assert_called_once_with(
    expected_text,
    flush=True
  )

@pytest.mark.parametrize(
  "show_in_terminal,substitute",
  [
    pytest.param(True, False),
    pytest.param(True, True)
  ],
)
def test_calls_print_when_calling_logger_without_file_and_without_substitution(
  show_in_terminal,
  substitute,
  __mock_substitute_lines,
  __mock_print
):
  logger = Logger()
  logger.set_allow_substitution(False)
  logger(__SAMPLE_TEXT, show_in_terminal=show_in_terminal, substitute=substitute)
  __mock_print.assert_called_once_with(
    __SAMPLE_TEXT,
    flush=True
  )

@pytest.mark.parametrize(
  "allow_substitution,substitute, stores",
  [
    pytest.param(False, False, False),
    pytest.param(False, True, False),
    pytest.param(True, False, False),
    pytest.param(True, True, True)
  ],
)
def test_sets_expected_last_printed_element_when_calling_logger(
  allow_substitution,
  substitute,
  stores,
  __mock_remove_non_printable,
  __mock_print
):
  logger = Logger()
  logger.set_allow_substitution(allow_substitution)
  logger(__SAMPLE_TEXT, show_in_terminal=False, substitute=substitute)
  last_printed_elem = logger._Logger__last_printed_elem
  expected_len = __mock_remove_non_printable(__SAMPLE_TEXT) if stores else None
  assert (
    last_printed_elem == expected_len
  ), get_assertion_message("stored last printed element", expected_len, last_printed_elem)

@pytest.mark.parametrize(
  "show_in_terminal,substitute",
  [
    pytest.param(False, False),
    pytest.param(False, True)
  ],
)
def test_does_not_call_print_when_calling_logger_without_file(
  show_in_terminal,
  substitute,
  __mock_print
):
  logger = Logger()
  logger(__SAMPLE_TEXT, show_in_terminal=show_in_terminal, substitute=substitute)
  __mock_print.assert_not_called()

def test_calls_print_when_calling_logger_with_file(
  __mock_open,
  __mock_remove_non_printable,
  __mock_print
):
  logger = Logger()
  logger.start_log_file("dummy_file_name")
  logger(__SAMPLE_TEXT, show_in_terminal=False)
  __mock_print.assert_called_once_with(
    __mock_remove_non_printable(__SAMPLE_TEXT),
    file=__mock_open(),
    flush=True
  )

def test_calls_stream_readline_when_logging_in_streaming(__mock_stream):
  __mock_stream.readline.side_effect = []
  logger = Logger()
  logger.log_in_streaming(__mock_stream)
  __mock_stream.readline.assert_called_once_with()

@pytest.mark.parametrize(
  "error,show_in_terminal,substitute",
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
def test_calls_logger_with_expected_params_when_logging_in_streaming(
  error,
  show_in_terminal,
  substitute,
  __mock_stream,
  __mock_call
):
  logger = Logger()
  logger.log_in_streaming(
    __mock_stream,
    show_in_terminal=show_in_terminal,
    substitute=substitute,
    err=error
  )
  __mock_call.assert_has_calls([
    call(
      logger.red(line) if error else line,
      show_in_terminal=show_in_terminal,
      substitute=substitute
    ) for line in __STREAM_READLINE_DECODED
  ])

def __get_substitution_chars(up_char: str, remove_line_char: str, n_lines: int):
  substitution_chars = ''
  for _ in range(n_lines):
    substitution_chars += f"{up_char}{remove_line_char}"
  return substitution_chars

@pytest.fixture
def __mock_reset_format():
  new_format_code = "-format_end"
  with patch.object(Logger, "_Logger__END_FORMAT", new_format_code):
    yield new_format_code

@pytest.fixture
def __mock_color_green():
  new_format_code = "green_start-"
  with patch.object(Logger, "_Logger__GREEN", new_format_code):
    yield new_format_code

@pytest.fixture
def __mock_color_yellow():
  new_format_code = "yellow_start-"
  with patch.object(Logger, "_Logger__YELLOW", new_format_code):
    yield new_format_code

@pytest.fixture
def __mock_color_red():
  new_format_code = "red_start-"
  with patch.object(Logger, "_Logger__RED", new_format_code):
    yield new_format_code

@pytest.fixture
def __mock_color_blue():
  new_format_code = "blue_start-"
  with patch.object(Logger, "_Logger__BLUE", new_format_code):
    yield new_format_code

@pytest.fixture
def __mock_bold():
  new_format_code = "bold_start-"
  with patch.object(Logger, "_Logger__BOLD", new_format_code):
    yield new_format_code

@pytest.fixture
def __mock_open():
  with patch("builtins.open") as mock_method:
    mock_method.return_value = __DUMMY_FILE
    yield mock_method

@pytest.fixture
def __mock_call():
  with patch("xmipp3_installer.application.logger.logger.Logger.__call__") as mock_method:
    yield mock_method

@pytest.fixture
def __mock_errors():
  with patch.object(errors, "ERROR_CODES", __ERROR_CODES):
    yield

@pytest.fixture(params=[0])
def __mock_get_terminal_column_size(request):
  with patch("shutil.get_terminal_size") as mock_method:
    mock_method.return_value = MockTerminalSize(request.param)
    yield mock_method

@pytest.fixture
def __mock_up():
  new_format_code = "up-"
  with patch.object(Logger, "_Logger__UP", new_format_code):
    yield new_format_code

@pytest.fixture
def __mock_remove_line():
  new_format_code = "line_remove-"
  with patch.object(Logger, "_Logger__REMOVE_LINE", new_format_code):
    yield new_format_code

@pytest.fixture(params=[0])
def __mock_get_n_last_lines(request):
  with patch("xmipp3_installer.application.logger.logger.Logger._Logger__get_n_last_lines") as mock_method:
    mock_method.return_value = request.param
    yield mock_method

@pytest.fixture
def __mock_print():
  with patch("builtins.print") as mock_method:
    yield mock_method

@pytest.fixture
def __mock_remove_non_printable():
  with patch("xmipp3_installer.application.logger.logger.Logger._Logger__remove_non_printable") as mock_method:
    mock_method.side_effect = lambda text: f"non_printable_affix-{text}-non_printable_affix"
    yield mock_method

@pytest.fixture
def __mock_substitute_lines():
  with patch("xmipp3_installer.application.logger.logger.Logger._Logger__substitute_lines") as mock_method:
    mock_method.side_effect = lambda text: f"substitute_lines_affix-{text}-non_printable_affix"
    yield mock_method

@pytest.fixture
def __mock_stream():
  mock_stream = Mock()
  mock_stream.readline.side_effect = __STREAM_READLINE
  return mock_stream
