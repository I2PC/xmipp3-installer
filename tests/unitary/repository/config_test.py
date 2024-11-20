from unittest.mock import patch, mock_open, Mock, call

import pytest

from xmipp3_installer.repository import config

from ... import get_assertion_message

__PATH = "/path/to/config.conf"
__DATE = "19/11/2024"
__FILE_LINES = [
	"line1\n",
	"line2\n",
	f"{config.__LAST_MODIFIED_TEXT}\n",
	f"{config.__LAST_MODIFIED_TEXT} {__DATE}\n",
	"line4\n"
]

def test_calls_open_when_getting_file_content(__mock_path_exists, __mock_open):
	config.__get_file_content(__PATH)
	__mock_open.assert_called_once_with(__PATH, "r")

def test_calls_file_readlines_when_getting_file_content(__mock_path_exists, __mock_open):
	config.__get_file_content(__PATH)
	__mock_open().readlines.assert_called_once_with()

@pytest.mark.parametrize(
	"__mock_path_exists,__mock_open,expected_content",
	[
		pytest.param(False, [], []),
		pytest.param(False, __FILE_LINES, []),
		pytest.param(True, [], []),
		pytest.param(True, __FILE_LINES, __FILE_LINES)
	],
	indirect=["__mock_path_exists", "__mock_open"]
)
def test_returns_expected_file_content(
	__mock_path_exists,
	__mock_open,
	expected_content
):
	content = config.__get_file_content(__PATH)
	assert (
		content == expected_content
	), get_assertion_message("file content", expected_content, content)

@pytest.mark.parametrize(
	"__mock_get_file_content",
	[
		pytest.param([]),
		pytest.param(__FILE_LINES[0:2])
	],
	indirect=["__mock_get_file_content"]
)
def test_does_not_call_re_search_with_empty_file_content_when_getting_config_date(
	__mock_get_file_content,
	__mock_re_search
):
	config.get_config_date(__PATH)
	__mock_re_search.assert_not_called()

def test_calls_re_search_when_getting_config_date(
	__mock_get_file_content,
	__mock_re_search
):
	__mock_re_search.return_value = None
	search_regex = r'\d{2}/\d{2}/\d{4}'
	config.get_config_date(__PATH)
	__mock_re_search.assert_has_calls([
		call(search_regex, __FILE_LINES[2]),
		call(search_regex, __FILE_LINES[3])
	])

@pytest.mark.parametrize(
	"__mock_get_file_content,expected_date",
	[
		pytest.param([], ""),
		pytest.param(__FILE_LINES[:2], ""),
		pytest.param(__FILE_LINES[:3], ""),
		pytest.param(__FILE_LINES[:4], __DATE),
		pytest.param(__FILE_LINES, __DATE)
	],
	indirect=["__mock_get_file_content"]
)
def test_returns_expected_config_date(
	__mock_get_file_content,
	expected_date
):
	config_date = config.get_config_date(__PATH)
	assert (
		config_date == expected_date
	), get_assertion_message("last configuration modification date", expected_date, config_date)

@pytest.mark.parametrize(
	"line,line_number",
	[
		pytest.param("aaaaaa", 0),
		pytest.param("whatever", 1),
		pytest.param("does-not-have-equal-separator", 5)
	]
)
def test_raises_exception_when_parsing_config_line_with_invalid_format(line, line_number):
	with pytest.raises(
		RuntimeError,
		match=f'Unable to parse line {line_number + 1}: {line}'
	):
		config.__parse_config_line(line, line_number)

@pytest.mark.parametrize(
	"line",
	[
		pytest.param(""),
		pytest.param(" "),
		pytest.param("\n"),
		pytest.param(" \n"),
		pytest.param("#"),
		pytest.param("# Test comment")
	]
)
def test_returns_none_when_parsing_config_line_with_no_data(line):
	parsed_line = config.__parse_config_line(line, 0)
	assert (
		parsed_line is None
	), get_assertion_message("parsed configuration file line", None, parsed_line)

@pytest.fixture(params=[True])
def __mock_path_exists(request):
	with patch("os.path.exists") as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(params=[__FILE_LINES])
def __mock_open(request):
	m_open = mock_open(read_data=''.join(request.param))
	with patch("builtins.open", m_open):
		yield m_open

@pytest.fixture(params=[__FILE_LINES])
def __mock_get_file_content(request):
	with patch("xmipp3_installer.repository.config.__get_file_content") as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(params=([""]))
def __mock_re_search(request):
	mock_groups = Mock()
	mock_groups.group.side_effect = request.param
	with patch("re.search") as mock_method:
		mock_method.return_value = mock_groups
		yield mock_method
