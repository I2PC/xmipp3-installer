from unittest.mock import patch

import pytest

from xmipp3_installer.application.cli.parsers.base_help_formatter import BaseHelpFormatter
from xmipp3_installer.application.cli import arguments
from xmipp3_installer.application.cli.parsers import format

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
		arguments.SHORT_VERSION: "param1-short",
		arguments.LONG_VERSION: "param1-long"
	},
	"param2": {
		arguments.SHORT_VERSION: "param2-short"
	},
	"param3": {
		arguments.LONG_VERSION: "param3-long"
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

@pytest.mark.parametrize(
	"key,expected_name",
	[
		pytest.param("param1", __PARAMS["param1"][arguments.SHORT_VERSION]),
		pytest.param("param2", __PARAMS["param2"][arguments.SHORT_VERSION]),
		pytest.param("param3", __PARAMS["param3"][arguments.LONG_VERSION]),
		pytest.param("param4", "")
	],
)
def test_returns_expected_param_first_name(
	key,
	expected_name,
	__setup_parser,
	__mock_params
):
	assert (
		__setup_parser._get_param_first_name(key) == expected_name
	), "Received different param first name than expected."

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
		assert (
			__setup_parser._get_help_separator() == expected_separator
		), "Received different help separator than expected."

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
	assert (
		__setup_parser._text_with_limits(previous_text, "test") == full_expected_text
	), "Received different text with limits than expected."

@pytest.fixture
def __setup_parser():
	yield BaseHelpFormatter("test")

@pytest.fixture
def __mock_modes():
	with patch.object(arguments, "MODES", __MODES):
		yield

@pytest.fixture
def __mock_params():
	with patch.object(arguments, "PARAMS", __PARAMS):
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
