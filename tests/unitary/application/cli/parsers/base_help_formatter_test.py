from unittest.mock import patch

import pytest

from xmipp3_installer.application.cli.parsers.base_help_formatter import BaseHelpFormatter
from xmipp3_installer.application.cli.arguments import modes, params
from xmipp3_installer.application.cli.parsers import format

from ..... import get_assertion_message

__MODES = {
	"group1": {
		"mode1": ["mode1-message1", "mode1-message2"],
		"mode2": ["mode2-message1", "mode2-message2", "mode2-message3"]
	},
	"group2": {
		"mode3": ["mode3-message1"]
	}
}
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

@pytest.mark.parametrize(
	"mode,general,expected_help_message",
	[
		pytest.param("mode1", True, "mode1-message1"),
		pytest.param("mode1", False, "mode1-message1\nmode1-message2"),
		pytest.param("mode2", True, "mode2-message1"),
		pytest.param("mode3", True, "mode3-message1"),
		pytest.param("mode3", False, "mode3-message1"),
		pytest.param("does-not-exist", False, ""),
		pytest.param("does-not-exist", True, "")
	],
)
def test_returns_expected_help_message(
	mode,
	general,
	expected_help_message,
	__setup_parser,
	__mock_modes
):
	help_message = __setup_parser._get_mode_help(mode, general=general)
	assert (
		help_message == expected_help_message
	), get_assertion_message("help message", expected_help_message, help_message)

@pytest.mark.parametrize(
	"key,expected_name",
	[
		pytest.param("param1", __PARAMS["param1"][params.SHORT_VERSION]),
		pytest.param("param2", __PARAMS["param2"][params.SHORT_VERSION]),
		pytest.param("param3", __PARAMS["param3"][params.LONG_VERSION]),
		pytest.param("param4", "")
	],
)
def test_returns_expected_param_first_name(
	key,
	expected_name,
	__setup_parser,
	__mock_params
):
	first_name = __setup_parser._get_param_first_name(key)
	assert (
		first_name == expected_name
	), get_assertion_message("param first name", expected_name, first_name)

@pytest.mark.parametrize(
	"n_dashes,__mock_tab_size,expected_separator",
	[
		pytest.param(2, 2, "  --\n"),
		pytest.param(0, 2, "  \n"),
		pytest.param(-1, 2, "  \n"),
		pytest.param(2, 0, "--\n"),
		pytest.param(0, 0, "\n"),
		pytest.param(-1, 0, "\n")
	],
	indirect=["__mock_tab_size"]
)
def test_gets_expected_help_separator(
	n_dashes,
	__mock_tab_size,
	expected_separator,
	__setup_parser
):
	with patch.object(BaseHelpFormatter, "_BaseHelpFormatter__SECTION_N_DASH", n_dashes):
		help_separator = __setup_parser._get_help_separator()
		assert (
			help_separator == expected_separator
		), get_assertion_message("help separator", expected_separator, help_separator)

def test_calls_get_spaces_when_getting_text_with_limits(
	__mock_get_spaces,
	__mock_multi_line_help_text,
	__setup_parser
):
	previous_text = "test-previous"
	__setup_parser._text_with_limits(previous_text, "test")
	__mock_get_spaces.assert_called_once_with(previous_text)

def test_calls_multi_line_help_text_when_getting_text_with_limits(
	__mock_get_spaces,
	__mock_multi_line_help_text,
	__mock_get_start_section_fill_in_space,
	__setup_parser
):
	previous_text = "test-previous"
	test_text = "test"
	remaining_spaces = 0
	__mock_get_spaces.return_value = (remaining_spaces, "fill-in")
	__setup_parser._text_with_limits(previous_text, test_text)
	__mock_multi_line_help_text.assert_called_once_with(
		test_text,
		remaining_spaces,
		__mock_get_start_section_fill_in_space()
	)

@pytest.mark.parametrize(
	"previous_text,__mock_get_spaces,__mock_multi_line_help_text,expected_text",
	[
		pytest.param("previous text", (0, ""), "", "previous text"),
		pytest.param("random", (1, "2"), "", "random2"),
		pytest.param("", (1, "2"), "", "2"),
		pytest.param("", (0, "2"), "", "2"),
		pytest.param("", (0, "2"), "test", "2test"),
		pytest.param("", (0, ""), "test", "test"),
		pytest.param("test", (1, "2"), "3", "test23")
	],
	indirect=["__mock_get_spaces", "__mock_multi_line_help_text"]
)
def test_gets_expected_text_with_limits(
	previous_text,
	__mock_get_spaces,
	__mock_multi_line_help_text,
	expected_text,
	__setup_parser
):
	full_expected_text = f"{expected_text}\n"
	text_with_limits = __setup_parser._text_with_limits(previous_text, "test")
	assert (
		text_with_limits == full_expected_text
	), get_assertion_message("text with limits", full_expected_text, text_with_limits)

def test_calls_formatting_tabs_when_getting_expected_text_len(
	__mock_get_formatting_tabs,
	__setup_parser
):
	test_text = "my text"
	__setup_parser._get_text_length(test_text)
	__mock_get_formatting_tabs.assert_called_once_with(test_text)

@pytest.mark.parametrize(
	"text,__mock_tab_size,expected_length",
	[
		pytest.param("", 0, 0),
		pytest.param("	", 2, 2),
		pytest.param("test", 0, 4),
		pytest.param("	test", 0, 4),
		pytest.param("	test", 1, 5)
	],
	indirect=["__mock_tab_size"]
)
def test_gets_expected_text_len(
	text,
	__mock_tab_size,
	expected_length,
	__setup_parser
):
	text_length = __setup_parser._get_text_length(text)
	assert (
		text_length == expected_length
	), get_assertion_message("text length", expected_length, text_length)

@pytest.mark.parametrize(
	"__mock_get_terminal_column_size,__mock_line_size_lower_limit,expected_size",
	[
		pytest.param(25, 10, 25),
		pytest.param(25, 25, 25),
		pytest.param(25, 26, 26),
		pytest.param(0, -1, 0),
		pytest.param(-1, -1, -1),
		pytest.param(-1, 0, 0)
	],
	indirect=["__mock_get_terminal_column_size", "__mock_line_size_lower_limit"]
)
def test_gets_expected_line_size(
	__mock_get_terminal_column_size,
	__mock_line_size_lower_limit,
	expected_size,
	__setup_parser
):
	line_size = __setup_parser._BaseHelpFormatter__get_line_size()
	assert (
		line_size == expected_size
	), get_assertion_message("line size", expected_size, line_size)
	
@pytest.mark.parametrize(
	"text,size_limit,left_fill,expected_formatted_text",
	[
		pytest.param("", 5, "", ""),
		pytest.param("test", 5, "", "test"),
		pytest.param("test", 5, "  ", "test"),
		pytest.param("test", 8, "  ", "test"),
		pytest.param("test test", 5, "", "test\ntest"),
		pytest.param("test", 2, "", "test"),
		pytest.param("test1 test2", 12, "  ", "test1 test2"),
		pytest.param("test1 test2", 8, "  ", "test1\n  test2"),
		pytest.param("test1 test2butlong", 8, "  ", "test1\n  test2butlong")
	],
)
def test_calls_format_text_in_lines_when_getting_multi_line_help_text(
	text,
	size_limit,
	left_fill,
	expected_formatted_text,
	__setup_parser
):
	formatted_text = __setup_parser._BaseHelpFormatter__multi_line_help_text(
		text,
		size_limit,
		left_fill
	)
	assert (
		formatted_text == expected_formatted_text
	), get_assertion_message("formatted text", expected_formatted_text, formatted_text)

@pytest.mark.parametrize(
	"text,__mock_section_help_start,expected_fill_in_space,expected_remaining_space",
	[
		pytest.param("test", 10, "      ", 70),
		pytest.param("testmaslargo", 10, " ", 68)
	],
	indirect=["__mock_section_help_start"]
)
def test_returns_expected_spaces(
	text,
	__mock_section_help_start,
	expected_fill_in_space,
	expected_remaining_space,
	__mock_get_line_size,
	__setup_parser
):
	__mock_get_line_size.return_value = 80
	remaining_space, fill_in_space = __setup_parser._BaseHelpFormatter__get_spaces(text)
	assert (
		(remaining_space, fill_in_space) == (expected_remaining_space, expected_fill_in_space)
	), get_assertion_message(
		"remaining space or fill in space",
		(expected_remaining_space, expected_fill_in_space),
		(remaining_space, fill_in_space)
	)

@pytest.fixture
def __setup_parser():
	yield BaseHelpFormatter("test")

@pytest.fixture
def __mock_modes():
	with patch.object(modes, "MODES", __MODES):
		yield

@pytest.fixture
def __mock_params():
	with patch.object(params, "PARAMS", __PARAMS):
		yield

@pytest.fixture
def __mock_tab_size(request):
	tab_size = request.param if hasattr(request, "param") else 2
	with patch.object(format, "TAB_SIZE", tab_size):
		yield

@pytest.fixture
def __mock_get_spaces(request):
	with patch(
		"xmipp3_installer.application.cli.parsers.base_help_formatter.BaseHelpFormatter._BaseHelpFormatter__get_spaces"
	) as mock_method:
		mock_method.return_value = request.param if hasattr(request, "param") else (1, '')
		yield mock_method

@pytest.fixture
def __mock_multi_line_help_text(request):
	with patch(
		"xmipp3_installer.application.cli.parsers.base_help_formatter.BaseHelpFormatter._BaseHelpFormatter__multi_line_help_text"
	) as mock_method:
		mock_method.return_value = request.param if hasattr(request, "param") else ''
		yield mock_method

@pytest.fixture
def __mock_get_start_section_fill_in_space():
	with patch(
		"xmipp3_installer.application.cli.parsers.base_help_formatter.BaseHelpFormatter._BaseHelpFormatter__get_start_section_fill_in_space"
	) as mock_method:
		mock_method.return_value = ""
		yield mock_method

@pytest.fixture
def __mock_get_formatting_tabs():
	with patch(
		"xmipp3_installer.application.cli.parsers.format.get_formatting_tabs"
	) as mock_method:
		yield mock_method

@pytest.fixture
def __mock_get_terminal_column_size(request):
	class MockTerminalSize:
		def __init__(self, columns):
			self.columns = columns
		def __iter__(self):
			return iter((self.columns, 5))
	with patch("shutil.get_terminal_size") as mock_method:
		mock_method.return_value = MockTerminalSize(
			request.param if hasattr(request, "param") else 25
		)
		yield mock_method

@pytest.fixture
def __mock_line_size_lower_limit(request):
	size = request.param if hasattr(request, "param") else 5
	with patch.object(BaseHelpFormatter, "_BaseHelpFormatter__LINE_SIZE_LOWER_LIMIT", size):
		yield

@pytest.fixture
def __mock_section_help_start(request):
	size = request.param if hasattr(request, "param") else 5
	with patch.object(BaseHelpFormatter, "_BaseHelpFormatter__SECTION_HELP_START", size):
		yield

@pytest.fixture
def __mock_get_line_size():
	with patch(
		"xmipp3_installer.application.cli.parsers.base_help_formatter.BaseHelpFormatter._BaseHelpFormatter__get_line_size"
	) as mock_method:
		yield mock_method
