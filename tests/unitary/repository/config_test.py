from datetime import datetime
from typing import Dict
from unittest.mock import patch, mock_open, Mock, call

import pytest

from xmipp3_installer.shared.singleton import Singleton
from xmipp3_installer.repository.config import ConfigurationFile
from xmipp3_installer.repository.invalid_config_line import InvalidConfigLineError
from xmipp3_installer.installer import constants
from xmipp3_installer.repository.config_vars import default_values, variables

from ... import get_assertion_message

__PATH = "/path/to/config.conf"
__DATE = "25-11-2024"
__DATE_TIME = datetime(2024, 11, 25, 1, 26, 46, 292469)
__FILE_LINES = [
	"line1\n",
	"line2\n",
	f"{ConfigurationFile._ConfigurationFile__LAST_MODIFIED_TEXT}\n",
	f"{ConfigurationFile._ConfigurationFile__LAST_MODIFIED_TEXT} {__DATE}\n",
	"line4\n"
]
__CORRECT_FILE_LINES = {
	"key=value",
	"mykey=test-value"
}
__TOGGLES_SECTION = "section1"
__LOCATIONS_SECTION = "section2"
__COMPILATION_FLAGS_SECTION = "section3"
__CONFIG_VARIABLES = {
	__TOGGLES_SECTION: [
		"variable1-section1", "variable2-section1", "variable3-section1"
	],
	__LOCATIONS_SECTION: [
		"variable1-section2", "variable2-section2", "variable3-section2"
	],
	__COMPILATION_FLAGS_SECTION: ["variable1-section3"]
}
__CONFIG_VALUES = {
	"variable1-section1": "test",
	"variable2-section1": "test2",
	"variable3-section1": "mytest",
	"variable1-section2": "section2-test",
	"variable3-section2": "section2-test3",
}
__DEFAULT_CONFIG_VALUES = {
	"variable1-section1": "default1-section1",
	"variable2-section1": "default2-section1",
	"variable3-section1": "default3-section1",
	"variable1-section2": "default1-section2",
	"variable2-section2": "default2-section2",
	"variable3-section2": "default3-section2",
	"variable1-section3": "default-section3"
}

def test_inherits_from_singleton_class(
		__mock_read_config,
		__mock_read_config_date
	):
	config_file = ConfigurationFile()
	assert isinstance(config_file, Singleton)

def test_sets_config_file_path_when_constructing_configuration_file_with_provided_value(
	__mock_read_config,
	__mock_read_config_date
):
	config_file = ConfigurationFile(__PATH)
	assert (
		config_file._ConfigurationFile__path == __PATH
	), get_assertion_message(
		"config file path",
		config_file._ConfigurationFile__path,
		__PATH
	)

def test_sets_config_file_path_when_constructing_configuration_file_with_default_value(
	__mock_read_config,
	__mock_read_config_date
):
	config_file = ConfigurationFile()
	assert (
		config_file._ConfigurationFile__path == constants.CONFIG_FILE
	), get_assertion_message(
		"config file path",
		config_file._ConfigurationFile__path,
		constants.CONFIG_FILE
	)

def test_sets_config_variables_when_constructing_configuration_file(
	__mock_read_config,
	__mock_read_config_date
):
	config_file = ConfigurationFile()
	assert (
		config_file.values == {}
	), get_assertion_message("config variables", config_file.values, {})

def test_calls_read_config_when_constructing_configuration_file(
	__mock_read_config,
	__mock_read_config_date
):
	ConfigurationFile()
	__mock_read_config.assert_called_once_with()

def test_calls_read_config_date_when_constructing_configuration_file(
	__mock_read_config,
	__mock_read_config_date
):
	ConfigurationFile()
	__mock_read_config_date.assert_called_once_with()

def test_calls_read_config_date_when_getting_config_date_and_is_not_set(
	__mock_init,
	__mock_read_config_date
):
	config_file = ConfigurationFile()
	config_file.last_modified = ""
	config_file.get_config_date()
	__mock_read_config_date.assert_called_once_with()

def test_does_not_call_read_config_date_when_getting_config_date_and_is_set(
	__mock_init,
	__mock_read_config_date
):
	config_file = ConfigurationFile()
	config_file.last_modified = "random-value"
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
def test_returns_expected_config_date_when_getting_config_date(
	initial_value,
	expected_value,
	__mock_init,
	__mock_read_config_date
):
	config_file = ConfigurationFile()
	config_file.last_modified = initial_value
	config_date = config_file.get_config_date()
	assert (
		config_date == expected_value
	), get_assertion_message("config date", expected_value, config_date)

def test_calls_file_readlines_when_getting_file_content(
	__mock_init,
	__mock_path_exists,
	__mock_open
):
	config_file = ConfigurationFile()
	config_file._ConfigurationFile__get_file_content()
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
	__mock_init,
	__mock_path_exists,
	__mock_open,
	expected_content
):
	config_file = ConfigurationFile()
	content = config_file._ConfigurationFile__get_file_content()
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
def test_does_not_call_re_search_with_empty_file_content_when_reading_config_date(
	__mock_init,
	__mock_get_file_content,
	__mock_re_search
):
	config_file = ConfigurationFile()
	config_file._ConfigurationFile__read_config_date()
	__mock_re_search.assert_not_called()

def test_calls_re_search_when_reading_config_date(
	__mock_init,
	__mock_get_file_content,
	__mock_re_search
):
	__mock_re_search.return_value = None
	config_file = ConfigurationFile()
	search_regex = r'\d{2}-\d{2}-\d{4}'
	config_file._ConfigurationFile__read_config_date()
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
def test_returns_expected_config_date_when_reading_config_date(
	__mock_init,
	__mock_get_file_content,
	expected_date
):
	config_file = ConfigurationFile()
	config_date = config_file._ConfigurationFile__read_config_date()
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
def test_raises_runtime_error_when_parsing_config_line_with_invalid_format(
	line,
	line_number,
	__mock_init,
	__mock_generate_invalid_config_line_error_message
):
	with pytest.raises(
		InvalidConfigLineError,
		match=__mock_generate_invalid_config_line_error_message(
			constants.CONFIG_FILE,
			line_number,
			line
		)
	):
		config_file = ConfigurationFile()
		config_file._ConfigurationFile__parse_config_line(line, line_number)

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
def test_returns_none_when_parsing_config_line_with_empty_data(
	line,
	__mock_init
):
	config_file = ConfigurationFile()
	parsed_line = config_file._ConfigurationFile__parse_config_line(line, 0)
	assert (
		parsed_line is None
	), get_assertion_message("parsed configuration file line", None, parsed_line)

@pytest.mark.parametrize(
	"line,expected_key,expected_value",
	[
		pytest.param("key=value", "key", "value"),
		pytest.param("test-key=test-value", "test-key", "test-value"),
		pytest.param("test-key=", "test-key", "")
	]
)
def test_returns_expected_key_value_pair_when_parsing_config_line(
	line,
	expected_key,
	expected_value,
	__mock_init
):
	config_file = ConfigurationFile()
	key_value_pair = config_file._ConfigurationFile__parse_config_line(line, 0)
	assert (
		key_value_pair == (expected_key, expected_value)
	), get_assertion_message("key-value pair", (expected_key, expected_value), key_value_pair)

@pytest.mark.parametrize(
	"key,value,default_value,expected_line",
	[
		pytest.param(None, None, None, ""),
		pytest.param(None, "", "", ""),
		pytest.param(None, "value", "default-value", ""),
		pytest.param("", None, None, ""),
		pytest.param("", "", "", ""),
		pytest.param("", "value", "default-value", ""),
		pytest.param("key", "value", "", "key=value"),
		pytest.param("key", "", "", "key="),
		pytest.param("key", "", "default-value", "key="),
		pytest.param("key", None, "", "key="),
		pytest.param(
			"key",
			None,
			"default-value",
			f"key{ConfigurationFile._ConfigurationFile__ASSIGNMENT_SEPARATOR}default-value"
		),
		pytest.param(
			"key",
			"value",
			"default-value",
			f"key{ConfigurationFile._ConfigurationFile__ASSIGNMENT_SEPARATOR}value"
		)
	]
)
def test_returns_expected_config_line_when_making_config_line(
	key,
	value,
	default_value,
	expected_line,
	__mock_init
):
	config_file = ConfigurationFile()
	config_line = config_file._ConfigurationFile__make_config_line(key, value, default_value)
	assert (
		config_line == expected_line
	), get_assertion_message("configuration file line", expected_line, config_line)

def test_calls_logger_when_reading_config_with_invalid_lines(
	__mock_init,
	__mock_get_file_content,
	__mock_generate_invalid_config_line_error_message,
	__mock_logger
):
	lines_with_wrong_data = [*__CORRECT_FILE_LINES, "aaaaa"]
	__mock_get_file_content.return_value = lines_with_wrong_data
	config_file = ConfigurationFile()
	config_file.read_config()
	__mock_logger.assert_called_once_with(str(InvalidConfigLineError(
		__mock_generate_invalid_config_line_error_message(
			constants.CONFIG_FILE,
			len(lines_with_wrong_data),
			lines_with_wrong_data[-1]
		))
	))

def test_returns_default_config_values_when_reading_config_with_invalid_lines(
	__mock_init,
	__mock_get_file_content,
	__mock_generate_invalid_config_line_error_message,
	__mock_logger
):
	__mock_get_file_content.return_value = [*__CORRECT_FILE_LINES, "aaaaa"]
	config_file = ConfigurationFile()
	config_file.read_config()
	assert (
		config_file.values == default_values.CONFIG_DEFAULT_VALUES
	), get_assertion_message(
		"config values",
		default_values.CONFIG_DEFAULT_VALUES,
		config_file.values
	)

@pytest.mark.parametrize(
	"__mock_get_file_content,expected_values",
	[
		pytest.param(["key1=test"], {**__DEFAULT_CONFIG_VALUES, "key1": "test"}),
		pytest.param(["newkey=newvalue"], {**__DEFAULT_CONFIG_VALUES, "newkey": "newvalue"}),
		pytest.param(
			__CORRECT_FILE_LINES, 
			{**__DEFAULT_CONFIG_VALUES, "key": "value", "mykey": "test-value"}
		),
		pytest.param(["# Comment line"], __DEFAULT_CONFIG_VALUES)
	],
	indirect=["__mock_get_file_content"]
)
def test_returns_expected_config_values_when_reading_config_with_valid_lines(
	__mock_get_file_content,
	expected_values,
	__mock_init
):
	config_file = ConfigurationFile()
	config_file.read_config()
	assert (
		config_file.values == expected_values
	), get_assertion_message("config values", expected_values, config_file.values)

def test_calls_make_config_line_when_getting_toggle_lines(
	__mock_init,
	__mock_config_variables,
	__mock_make_config_line
):
	config_file = ConfigurationFile()
	for section in __CONFIG_VARIABLES.keys():
		config_file._ConfigurationFile__get_toggle_lines(
			section,
			__CONFIG_VALUES.copy()
		)
		__mock_make_config_line.assert_has_calls([
			call(
				section_variable,
				__CONFIG_VALUES.get(section_variable),
				__DEFAULT_CONFIG_VALUES[section_variable]
			)
			for section_variable in __CONFIG_VARIABLES[section]
		])

def test_removes_keys_from_dictionary_when_getting_toggle_lines(
	__mock_init,
	__mock_config_variables,
	__mock_make_config_line
):
	config_file = ConfigurationFile()
	config_values = __CONFIG_VALUES.copy()
	for section in __CONFIG_VARIABLES.keys():
		config_file._ConfigurationFile__get_toggle_lines(
			section,
			config_values
		)
		for section_variable in __CONFIG_VARIABLES[section]:
			assert (
				config_values.get(section_variable) is None
			), f"Item {section_variable} not deleted from dictionary {config_values}"

def test_returns_expected_lines_when_getting_toggle_lines(
	__mock_init,
	__mock_config_variables,
	__mock_make_config_line
):
	config_file = ConfigurationFile()
	for section in __CONFIG_VARIABLES.keys():
		section_lines = config_file._ConfigurationFile__get_toggle_lines(
			section,
			__CONFIG_VALUES.copy()
		)
		expected_lines = [
			f"{__mock_make_config_line(
				section_variable,
				__CONFIG_VALUES.get(section_variable),
				__DEFAULT_CONFIG_VALUES[section_variable]
			)}\n" for section_variable in __CONFIG_VARIABLES[section]
		]
		assert (
			section_lines == expected_lines
		), get_assertion_message("configuration file lines", expected_lines, section_lines)

def test_calls_make_config_line_when_getting_unkown_variable_lines(
	__mock_init,
	__mock_make_config_line
):
	config_file = ConfigurationFile()
	config_file._ConfigurationFile__get_unkown_variable_lines(
		__CONFIG_VALUES.copy()
	)
	__mock_make_config_line.assert_has_calls([
		call(
			unknown_variable,
			__CONFIG_VALUES[unknown_variable],
			""
		)
		for unknown_variable in __CONFIG_VALUES
	])

def test_returns_expected_lines_when_getting_unkown_variable_lines(
	__mock_init,
	__mock_make_config_line
):
	config_file = ConfigurationFile()
	lines = config_file._ConfigurationFile__get_unkown_variable_lines(
		__CONFIG_VALUES.copy()
	)
	expected_lines = [
		f"{__mock_make_config_line(
			unknown_variable,
			__CONFIG_VALUES[unknown_variable],
			""
		)}\n"
		for unknown_variable in __CONFIG_VALUES
	]
	assert (
		lines == expected_lines
	), get_assertion_message("unknown variable lines", expected_lines, lines)

def test_calls_get_toggle_lines_when_writing_config(
	__mock_read_config,
	__mock_read_config_date,
	__mock_config_toggles,
	__mock_config_locations,
	__mock_config_flags,
	__mock_get_toggle_lines,
	__mock_open
):
	call_params = []
	def __record_input_params_in_mock(section: str, variables: Dict):
		call_params.append((section, variables.copy()))
		return __mimick_get_toggle_lines(section, variables)
	__mock_get_toggle_lines.side_effect = __record_input_params_in_mock
	values_after_toggles = {
		k:v for k,v in __CONFIG_VALUES.items() if k not in __CONFIG_VARIABLES[__TOGGLES_SECTION]
	}
	values_after_locations = {
		k:v for k,v in values_after_toggles.items() if k not in __CONFIG_VARIABLES[__LOCATIONS_SECTION]
	}
	expected_call_params = [
		(__mock_config_toggles, __CONFIG_VALUES),
		(__mock_config_locations, values_after_toggles),
		(__mock_config_flags, values_after_locations)
	]
	config_file = ConfigurationFile()
	config_file.values = __CONFIG_VALUES.copy()
	config_file.write_config()
	assert (
		call_params == expected_call_params
	), get_assertion_message(
		"call params for function __get_toggle_lines",
		expected_call_params,
		call_params
	)

def test_calls_open_when_writing_config(
	__mock_read_config,
	__mock_read_config_date,
	__mock_get_toggle_lines,
	__mock_open
):
	config_file = ConfigurationFile()
	config_file.values = __CONFIG_VALUES.copy()
	config_file.write_config()
	__mock_open.assert_called_once_with(
		config_file._ConfigurationFile__path,
		'w'
	)

def test_calls_today_strftime_when_writing_config(
	__mock_read_config,
	__mock_read_config_date,
	__mock_get_toggle_lines,
	__mock_datetime_today,
	__mock_open
):
	config_file = ConfigurationFile()
	config_file.values = __CONFIG_VALUES.copy()
	config_file.write_config()
	__mock_datetime_today.today.assert_called_once_with()

def test_calls_strftime_when_writing_config(
	__mock_read_config,
	__mock_read_config_date,
	__mock_get_toggle_lines,
	__mock_datetime_strftime,
	__mock_open
):
	config_file = ConfigurationFile()
	config_file.values = __CONFIG_VALUES.copy()
	config_file.write_config()
	__mock_datetime_strftime.today().strftime.assert_called_once_with('%d-%m-%Y')

def __mimick_get_toggle_lines(section: str, variables: Dict):
	variables_copy = variables.copy()
	for variable in variables_copy.keys():
		if variable in __CONFIG_VARIABLES[section]:
			variables.pop(variable, None)
	return [f"Lines for section {section}"]

@pytest.fixture
def __mock_read_config():
	with patch(
		"xmipp3_installer.repository.config.ConfigurationFile.read_config"
	) as mock_method:
		yield mock_method

@pytest.fixture
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
	with patch(
		"xmipp3_installer.repository.config.ConfigurationFile._ConfigurationFile__get_file_content"
	) as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(params=([""]))
def __mock_re_search(request):
	mock_groups = Mock()
	mock_groups.group.side_effect = request.param
	with patch("re.search") as mock_method:
		mock_method.return_value = mock_groups
		yield mock_method

@pytest.fixture
def __mock_generate_invalid_config_line_error_message():
	side_effect = lambda conf_file, line_number, line: f"{conf_file} - {line_number} - {line}"
	with patch(
		"xmipp3_installer.repository.invalid_config_line.InvalidConfigLineError.generate_error_message"
	) as mock_method:
		mock_method.side_effect = side_effect
		yield mock_method

@pytest.fixture
def __mock_logger():
	with patch(
		"xmipp3_installer.application.logger.logger.Logger.__call__"
	) as mock_method:
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_config_default_variables():
	with patch.object(
		default_values,
		"CONFIG_DEFAULT_VALUES",
		__DEFAULT_CONFIG_VALUES
	) as mock_method:
		yield mock_method

@pytest.fixture
def __mock_config_variables():
	with patch.object(
		variables,
		"CONFIG_VARIABLES",
		__CONFIG_VARIABLES
	) as mock_object:
		yield mock_object

@pytest.fixture
def __mock_make_config_line():
	side_effect = lambda key, value, default_value: f"{key}-{value}-{default_value}"
	with patch(
		"xmipp3_installer.repository.config.ConfigurationFile._ConfigurationFile__make_config_line"
	) as mock_method:
		mock_method.side_effect = side_effect
		yield mock_method

@pytest.fixture
def __mock_get_toggle_lines():
	with patch(
		"xmipp3_installer.repository.config.ConfigurationFile._ConfigurationFile__get_toggle_lines"
	) as mock_method:
		yield mock_method

@pytest.fixture
def __mock_config_toggles():
	with patch.object(
		variables, "TOGGLES", __TOGGLES_SECTION
	) as mock_object:
		yield mock_object

@pytest.fixture
def __mock_config_locations():
	with patch.object(
		variables, "LOCATIONS", __LOCATIONS_SECTION
	) as mock_object:
		yield mock_object

@pytest.fixture
def __mock_config_flags():
	with patch.object(
		variables, "COMPILATION_FLAGS", __COMPILATION_FLAGS_SECTION
	) as mock_object:
		yield mock_object

@pytest.fixture
def __mock_datetime_today():
	with patch("xmipp3_installer.repository.config.datetime") as mock_lib:
		mock_lib.today.return_value = __DATE_TIME
		yield mock_lib

@pytest.fixture
def __mock_datetime_strftime():
	with patch("xmipp3_installer.repository.config.datetime") as mock_lib:
		mock_today = Mock()
		mock_today.strftime.return_value = __DATE
		mock_lib.today.return_value = mock_today
		yield mock_lib
