import os
import tempfile
from typing import List
from unittest.mock import patch, Mock

import pytest

from xmipp3_installer.repository.config_vars import variables, default_values, config_values_adapter
from xmipp3_installer.repository.config import ConfigurationFileHandler

from . import file_content
from .... import get_assertion_message

__ASSERTION_CONTEXT = "config file content"

def test_writes_default_config_when_there_is_no_config_file(
	__mock_config_file,
	__mock_datetime_strftime
):
	config_handler = ConfigurationFileHandler(__mock_config_file.name)
	config_handler.write_config()
	config_file_content = ''.join(
		config_handler._ConfigurationFileHandler__get_file_content()
	).splitlines()
	config_file_content = __change_config_cmake_path(config_file_content)
	assert (
		config_file_content == file_content.DEFAULT_FILE_LINES
	), get_assertion_message(
		__ASSERTION_CONTEXT,
		file_content.DEFAULT_FILE_LINES,
		config_file_content
	)

@pytest.mark.parametrize(
	"__mock_environment",
	[
		pytest.param(
			(f"{variables.ENVIRONMENT_VARIABLES_PREFIX}{variables.CUDA}", default_values.ON),
			id="CUDA on"
		),
		pytest.param(
			(f"{variables.ENVIRONMENT_VARIABLES_PREFIX}{variables.CUDA}", default_values.OFF),
			id="CUDA off"
		),
		pytest.param(
			(f"{variables.ENVIRONMENT_VARIABLES_PREFIX}{variables.CMAKE}", "/path/to/cmake"),
			id="CMAKE path"
		)
	],
	indirect=["__mock_environment"]
)
def test_overwrites_config_values_with_environment_values(
	__mock_config_file,
	__mock_datetime_strftime,
	__mock_environment
):
	variable, new_raw_value = __mock_environment
	expected_value = config_values_adapter.get_context_values_from_file_values(
		{variable: new_raw_value}
	)[variable]
	config_handler = ConfigurationFileHandler(__mock_config_file.name)
	assert (
		config_handler.values[variable] == expected_value
	)

def test_writes_unkown_variables_to_config_when_unkown_variables_are_added_to_values(
	__mock_config_file,
	__mock_datetime_strftime
):
	unknown_key = "UNKNOWN"
	unknown_value = "myvalue"
	config_handler = ConfigurationFileHandler(__mock_config_file.name)
	config_handler.values.update({unknown_key: unknown_value})
	config_handler.write_config()
	config_file_content = ''.join(
		config_handler._ConfigurationFileHandler__get_file_content()
	).splitlines()
	expected_file_content = [
		*file_content.MANDATORY_SECTIONS_LINES,
		*file_content.UNKNOWN_VARIABLES_HEADER,
		f"{unknown_key}={unknown_value}",
		"",
		file_content.LAST_MODIFIED_LINE
	]
	config_file_content = __change_config_cmake_path(config_file_content)
	assert (
		config_file_content == expected_file_content
	), get_assertion_message(
		__ASSERTION_CONTEXT,
		expected_file_content,
		config_file_content
	)

def test_writes_modified_variables_to_config_when_some_variable_values_are_changed(
	__mock_config_file,
	__mock_datetime_strftime
):
	modified_key = "SEND_INSTALLATION_STATISTICS"
	config_handler = ConfigurationFileHandler(__mock_config_file.name)
	config_handler.values.update({modified_key: False})
	config_handler.write_config()
	config_file_content = ''.join(
		config_handler._ConfigurationFileHandler__get_file_content()
	).splitlines()
	expected_file_content = '\n'.join(
		file_content.DEFAULT_FILE_LINES
	).replace(f"{modified_key}=ON", f"{modified_key}=OFF").splitlines()
	config_file_content = __change_config_cmake_path(config_file_content)
	assert (
		config_file_content == expected_file_content
	), get_assertion_message(
		__ASSERTION_CONTEXT,
		expected_file_content,
		config_file_content
	)

def test_returns_class_stored_last_modification_date_over_file_stored_one(
	__mock_config_file,
	__mock_datetime_strftime
):
	config_handler = ConfigurationFileHandler(__mock_config_file.name)
	config_handler.write_config()
	config_handler.last_modified = file_content.DATE_2
	stored_date = config_handler.get_config_date()
	assert (
		stored_date == file_content.DATE_2
	), get_assertion_message("last modified date", file_content.DATE_2, stored_date)

def test_returns_file_stored_last_modification_date_when_there_is_no_value_stored(
	__mock_config_file,
	__mock_datetime_strftime
):
	config_handler = ConfigurationFileHandler(__mock_config_file.name)
	config_handler.write_config()
	config_handler.last_modified = ""
	stored_date = config_handler.get_config_date()
	assert (
		stored_date == __mock_datetime_strftime.today().strftime()
	), get_assertion_message(
		"last modified date",
		__mock_datetime_strftime.today().strftime(),
		stored_date
	)

def __change_config_cmake_path(content_lines: List[str]):
	new_lines = []
	for line in content_lines:
		new_line = line
		if line.startswith(variables.PREFIX_PATH):
			new_line = f"{variables.PREFIX_PATH}="
		new_lines.append(new_line)
	return new_lines

@pytest.fixture
def __mock_config_file():
	with tempfile.NamedTemporaryFile(
		delete=False,
		dir=os.path.dirname(os.path.abspath(__file__))
	) as temp_file:
		try:
			yield temp_file
		finally:
			temp_file.close()
			os.remove(temp_file.name)

@pytest.fixture
def __mock_datetime_strftime():
	with patch("xmipp3_installer.repository.config.datetime") as mock_lib:
		mock_today = Mock()
		mock_today.strftime.return_value = file_content.DATE
		mock_lib.today.return_value = mock_today
		yield mock_lib

@pytest.fixture(params=[("DUMMY_VAR", "DUMMT_VAL")])
def __mock_environment(request, monkeypatch):
	stored_name = request.param[0].replace(variables.ENVIRONMENT_VARIABLES_PREFIX, "")
	monkeypatch.setenv(request.param[0], request.param[1])
	yield stored_name, request.param[1]
