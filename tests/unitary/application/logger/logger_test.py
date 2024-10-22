from unittest.mock import patch

import pytest

from xmipp3_installer.application.logger.logger import Logger

from .... import get_assertion_message

__SAMPLE_TEXT = "this is some sample text"

def test_returns_new_instance(__mock_singleton):
	logger1 = Logger()
	with patch.object(Logger, "_Logger__instance", None):
		logger2 = Logger()
	assert (
		logger1 is not logger2
	), "Received same logger instance, when should have been different."

def test_returns_same_instance(__mock_singleton):
	logger1 = Logger()
	logger2 = Logger()
	assert (
		logger1 is logger2
	), get_assertion_message("Logger instance", logger1, logger2)

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

def test_calls_start_log_file(__mock_open, __mock_singleton):
	log_file_name = "test_log_file"
	logger = Logger()
	logger.start_log_file(log_file_name)
	__mock_open.assert_called_once_with(log_file_name, 'w')

def test_starts_log_file(__mock_open, __mock_singleton):
	logger = Logger()
	logger.start_log_file("test_log_file")
	assert (
		logger._Logger__log_file is not None
	), "Log file did not get properly assigned"

@pytest.mark.parametrize(
	"expected_console_output",
	[
		pytest.param(False),
		pytest.param(True)
	],
)
def test_sets_console_output(expected_console_output, __mock_singleton):
	logger = Logger()
	logger.set_console_output(expected_console_output)
	console_output = logger._Logger__output_to_console
	assert (
		console_output == expected_console_output
	), get_assertion_message("console output value", expected_console_output, console_output)

@pytest.mark.parametrize(
	"expected_allow_substitution",
	[
		pytest.param(False),
		pytest.param(True)
	],
)
def test_sets_allow_substitution(expected_allow_substitution, __mock_singleton):
	logger = Logger()
	logger.set_allow_substitution(expected_allow_substitution)
	allow_substitution = logger._Logger__allow_substitution
	assert (
		allow_substitution == expected_allow_substitution
	), get_assertion_message("allow substitution value", expected_allow_substitution, allow_substitution)

@pytest.fixture
def __mock_singleton():
	with patch.object(Logger, "_Logger__instance", None):
		yield

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
		yield mock_method
