from unittest.mock import patch, mock_open, Mock, call

import pytest

from xmipp3_installer.shared.singleton import Singleton
from xmipp3_installer.repository.config import ConfigurationFile
from xmipp3_installer.repository.invalid_config_line import InvalidConfigLineError
from xmipp3_installer.installer import constants
from xmipp3_installer.repository.config_vars import default_values

from ... import get_assertion_message

__PATH = "/path/to/config.conf"
__DATE = "19/11/2024"
__FILE_LINES = [
	"line1\n",
	"line2\n",
	#f"{config.__LAST_MODIFIED_TEXT}\n",
	#f"{config.__LAST_MODIFIED_TEXT} {__DATE}\n",
	"line4\n"
]
__CORRECT_FILE_LINES = {
	"key=value",
	"mykey=test-value"
}
__DEFAULT_CONFIG_VALUES = {
	"key1": "default-key1-value",
	"key2": "default-key2-value"
}

def test_inherits_from_singleton_class():
	config_file = ConfigurationFile()
	assert isinstance(config_file, Singleton)

def test_sets_config_file_path_when_constructing_configuration_file_with_provided_value():
	config_file = ConfigurationFile(__PATH)
	assert (
		config_file._ConfigurationFile__path == __PATH
	), get_assertion_message(
		"config file path",
		config_file._ConfigurationFile__path,
		__PATH
	)

def test_sets_config_file_path_when_constructing_configuration_file_with_default_value():
	config_file = ConfigurationFile()
	assert (
		config_file._ConfigurationFile__path == constants.CONFIG_FILE
	), get_assertion_message(
		"config file path",
		config_file._ConfigurationFile__path,
		constants.CONFIG_FILE
	)

def test_sets_config_variables_when_constructing_configuration_file():
	config_file = ConfigurationFile()
	assert (
		config_file.config_variables == {}
	), get_assertion_message("config variables", config_file.config_variables, {})

def test_calls_read_config_when_constructing_configuration_file(
	__mock_read_config
):
	ConfigurationFile()
	__mock_read_config.assert_called_once_with()

def test_calls_read_config_date_when_constructing_configuration_file(
	__mock_read_config_date
):
	ConfigurationFile()
	__mock_read_config_date.assert_called_once_with()

def test_calls_read_config_date_when_getting_config_date_and_is_not_set(
	__mock_init,
	__mock_read_config_date
):
	config_file = ConfigurationFile()
	config_file.config_date = ""
	config_file.get_config_date()
	__mock_read_config_date.assert_called_once_with()

def test_does_not_call_read_config_date_when_getting_config_date_and_is_set(
	__mock_init,
	__mock_read_config_date
):
	config_file = ConfigurationFile()
	config_file.config_date = "random-value"
	config_file.get_config_date()
	__mock_read_config_date.assert_not_called()

@pytest.mark.parametrize(
	"initial_value,expected_value",
	[
		pytest.param(None, __DATE),
		pytest.param("", __DATE),
		pytest.param("00-00-0000", "00-00-0000")
	]
)
def test_returns_expected_config_date(
	initial_value,
	expected_value,
	__mock_init,
	__mock_read_config_date
):
	config_file = ConfigurationFile()
	config_file.config_date = initial_value
	config_date = config_file.get_config_date()
	assert (
		config_date == expected_value
	), get_assertion_message("config date", expected_value, config_date)

#def test_calls_file_readlines_when_getting_file_content(__mock_path_exists, __mock_open):
#	config.__get_file_content(__PATH)
#	__mock_open().readlines.assert_called_once_with()
#
#@pytest.mark.parametrize(
#	"__mock_path_exists,__mock_open,expected_content",
#	[
#		pytest.param(False, [], []),
#		pytest.param(False, __FILE_LINES, []),
#		pytest.param(True, [], []),
#		pytest.param(True, __FILE_LINES, __FILE_LINES)
#	],
#	indirect=["__mock_path_exists", "__mock_open"]
#)
#def test_returns_expected_file_content(
#	__mock_path_exists,
#	__mock_open,
#	expected_content
#):
#	content = config.__get_file_content(__PATH)
#	assert (
#		content == expected_content
#	), get_assertion_message("file content", expected_content, content)
#
#@pytest.mark.parametrize(
#	"__mock_get_file_content",
#	[
#		pytest.param([]),
#		pytest.param(__FILE_LINES[0:2])
#	],
#	indirect=["__mock_get_file_content"]
#)
#def test_does_not_call_re_search_with_empty_file_content_when_getting_config_date(
#	__mock_get_file_content,
#	__mock_re_search
#):
#	config.get_config_date(__PATH)
#	__mock_re_search.assert_not_called()
#
#def test_calls_re_search_when_getting_config_date(
#	__mock_get_file_content,
#	__mock_re_search
#):
#	__mock_re_search.return_value = None
#	search_regex = r'\d{2}/\d{2}/\d{4}'
#	config.get_config_date(__PATH)
#	__mock_re_search.assert_has_calls([
#		call(search_regex, __FILE_LINES[2]),
#		call(search_regex, __FILE_LINES[3])
#	])
#
#@pytest.mark.parametrize(
#	"__mock_get_file_content,expected_date",
#	[
#		pytest.param([], ""),
#		pytest.param(__FILE_LINES[:2], ""),
#		pytest.param(__FILE_LINES[:3], ""),
#		pytest.param(__FILE_LINES[:4], __DATE),
#		pytest.param(__FILE_LINES, __DATE)
#	],
#	indirect=["__mock_get_file_content"]
#)
#def test_returns_expected_config_date(
#	__mock_get_file_content,
#	expected_date
#):
#	config_date = config.get_config_date(__PATH)
#	assert (
#		config_date == expected_date
#	), get_assertion_message("last configuration modification date", expected_date, config_date)
#
#@pytest.mark.parametrize(
#	"line,line_number",
#	[
#		pytest.param("aaaaaa", 0),
#		pytest.param("whatever", 1),
#		pytest.param("does-not-have-equal-separator", 5)
#	]
#)
#def test_raises_runtime_error_when_parsing_config_line_with_invalid_format(
#	line,
#	line_number,
#	__mock_generate_invalid_config_line_error_message
#):
#	with pytest.raises(
#		InvalidConfigLineError,
#		match=__mock_generate_invalid_config_line_error_message(
#			constants.CONFIG_FILE,
#			line_number,
#			line
#		)
#	):
#		config.__parse_config_line(line, line_number)
#
#@pytest.mark.parametrize(
#	"line",
#	[
#		pytest.param(""),
#		pytest.param(" "),
#		pytest.param("\n"),
#		pytest.param(" \n"),
#		pytest.param("#"),
#		pytest.param("# Test comment")
#	]
#)
#def test_returns_none_when_parsing_config_line_with_empty_data(line):
#	parsed_line = config.__parse_config_line(line, 0)
#	assert (
#		parsed_line is None
#	), get_assertion_message("parsed configuration file line", None, parsed_line)
#
#@pytest.mark.parametrize(
#	"line,expected_key,expected_value",
#	[
#		pytest.param("key=value", "key", "value"),
#		pytest.param("test-key=test-value", "test-key", "test-value"),
#		pytest.param("test-key=", "test-key", "")
#	]
#)
#def test_returns_expected_key_value_pair_when_parsing_config_line(
#	line,
#	expected_key,
#	expected_value
#):
#	key_value_pair = config.__parse_config_line(line, 0)
#	assert (
#		key_value_pair == (expected_key, expected_value)
#	), get_assertion_message("key-value pair", (expected_key, expected_value), key_value_pair)
#
#@pytest.mark.parametrize(
#	"key,value,default_value,expected_line",
#	[
#		pytest.param(None, None, None, ""),
#		pytest.param(None, "", "", ""),
#		pytest.param(None, "value", "default-value", ""),
#		pytest.param("", None, None, ""),
#		pytest.param("", "", "", ""),
#		pytest.param("", "value", "default-value", ""),
#		pytest.param("key", "value", "", "key=value"),
#		pytest.param("key", "", "", "key="),
#		pytest.param("key", "", "default-value", "key="),
#		pytest.param("key", None, "", "key="),
#		pytest.param("key", None, "default-value", f"key{config.__ASSIGNMENT_SEPARATOR}default-value"),
#		pytest.param("key", "value", "default-value", f"key{config.__ASSIGNMENT_SEPARATOR}value")
#	]
#)
#def test_returns_expected_config_line_when_making_config_line(
#	key,
#	value,
#	default_value,
#	expected_line
#):
#	config_line = config.__make_config_line(key, value, default_value)
#	assert (
#		config_line == expected_line
#	), get_assertion_message("configuration file line", expected_line, config_line)
#
#def test_calls_logger_when_reading_config_with_invalid_lines(
#	__mock_get_file_content,
#	__mock_generate_invalid_config_line_error_message,
#	__mock_logger
#):
#	lines_with_wrong_data = [*__CORRECT_FILE_LINES, "aaaaa"]
#	__mock_get_file_content.return_value = lines_with_wrong_data
#	config.read_config(__PATH)
#	__mock_logger.assert_called_once_with(str(InvalidConfigLineError(
#		__mock_generate_invalid_config_line_error_message(
#			constants.CONFIG_FILE,
#			len(lines_with_wrong_data),
#			lines_with_wrong_data[-1]
#		))
#	))
#
#def test_returns_default_config_values_when_reading_config_with_invalid_lines(
#	__mock_get_file_content,
#	__mock_generate_invalid_config_line_error_message,
#	__mock_logger
#):
#	__mock_get_file_content.return_value = [*__CORRECT_FILE_LINES, "aaaaa"]
#	config_values = config.read_config(__PATH)
#	assert (
#		config_values == default_values.CONFIG_DEFAULT_VALUES
#	), get_assertion_message(
#		"config values",
#		default_values.CONFIG_DEFAULT_VALUES,
#		config_values
#	)
#
#@pytest.mark.parametrize(
#	"file_lines,expected_values",
#	[
#		pytest.param(["key1=test"], {**__DEFAULT_CONFIG_VALUES, "key1": "test"}),
#		pytest.param(["newkey=newvalue"], {**__DEFAULT_CONFIG_VALUES, "newkey": "newvalue"}),
#		pytest.param(
#			__CORRECT_FILE_LINES, 
#			{**__DEFAULT_CONFIG_VALUES, "key": "value", "mykey": "test-value"}
#		),
#		pytest.param(["# Comment line"], __DEFAULT_CONFIG_VALUES)
#	]
#)
#def test_returns_expected_config_values_when_reading_config_with_invalid_lines(
#	file_lines,
#	expected_values,
#	__mock_get_file_content
#):
#	__mock_get_file_content.return_value = file_lines
#	config_values = config.read_config(__PATH)
#	assert (
#		config_values == expected_values
#	), get_assertion_message("config values", expected_values, config_values)

@pytest.fixture(autouse=True)
def __mock_read_config():
	with patch(
		"xmipp3_installer.repository.config.ConfigurationFile.read_config"
	) as mock_method:
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_read_config_date():
	with patch(
		"xmipp3_installer.repository.config.ConfigurationFile._ConfigurationFile__read_config_date",
		return_value=__DATE
	) as mock_method:
		yield mock_method

@pytest.fixture
def __mock_init():
	with patch(
		"xmipp3_installer.repository.config.ConfigurationFile.__init__",
		return_value=None
	) as mock_method:
		yield mock_method

#@pytest.fixture(params=[True])
#def __mock_path_exists(request):
#	with patch("os.path.exists") as mock_method:
#		mock_method.return_value = request.param
#		yield mock_method

#@pytest.fixture(params=[__FILE_LINES])
#def __mock_open(request):
#	m_open = mock_open(read_data=''.join(request.param))
#	with patch("builtins.open", m_open):
#		yield m_open

#@pytest.fixture(params=[__FILE_LINES])
#def __mock_get_file_content(request):
#	with patch(
#		"xmipp3_installer.repository.config.ConfigurationFile._ConfigurationFile__get_file_content"
#	) as mock_method:
#		mock_method.return_value = request.param
#		yield mock_method

#@pytest.fixture(params=([""]))
#def __mock_re_search(request):
#	mock_groups = Mock()
#	mock_groups.group.side_effect = request.param
#	with patch("re.search") as mock_method:
#		mock_method.return_value = mock_groups
#		yield mock_method

#@pytest.fixture
#def __mock_logger():
#	with patch(
#		"xmipp3_installer.application.logger.logger.Logger.__call__"
#	) as mock_method:
#		yield mock_method

#@pytest.fixture
#def __mock_generate_invalid_config_line_error_message():
#	side_effect = lambda conf_file, line_number, line: f"{conf_file} - {line_number} - {line}"
#	with patch(
#		"xmipp3_installer.repository.invalid_config_line.InvalidConfigLineError.generate_error_message"
#	) as mock_method:
#		mock_method.side_effect = side_effect
#		yield mock_method

#@pytest.fixture(autouse=True)
#def __mock_config_default_variables():
#	with patch.object(
#		default_values,
#		"CONFIG_DEFAULT_VALUES",
#		__DEFAULT_CONFIG_VALUES
#	) as mock_method:
#		yield mock_method