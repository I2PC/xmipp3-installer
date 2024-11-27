import os
import tempfile
from unittest.mock import patch, Mock

import pytest

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
	).split("\n")
	assert (
		config_file_content == file_content.DEFAULT_FILE_LINES
	), get_assertion_message(
		__ASSERTION_CONTEXT,
		file_content.DEFAULT_FILE_LINES,
		config_file_content
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
	).split("\n")
	expected_file_content = [
		*file_content.MANDATORY_SECTIONS_LINES,
		*file_content.UNKNOWN_VARIABLES_HEADER,
		f"{unknown_key}={unknown_value}",
		"",
		*file_content.LAST_MODIFIED_LINES
	]
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
	modified_value = "OFF"
	config_handler = ConfigurationFileHandler(__mock_config_file.name)
	config_handler.values.update({modified_key: modified_value})
	config_handler.write_config()
	config_file_content = ''.join(
		config_handler._ConfigurationFileHandler__get_file_content()
	).split("\n")
	expected_file_content = '\n'.join(
		file_content.DEFAULT_FILE_LINES
	).replace(f"{modified_key}=ON", f"{modified_key}={modified_value}").split("\n")
	assert (
		config_file_content == expected_file_content
	), get_assertion_message(
		__ASSERTION_CONTEXT,
		expected_file_content,
		config_file_content
	)

@pytest.fixture
def __mock_config_file():
	with tempfile.NamedTemporaryFile(
		delete=True,
		delete_on_close=False,
		dir=os.path.dirname(os.path.abspath(__file__))
	) as temp_file:
		yield temp_file

@pytest.fixture
def __mock_datetime_strftime():
	with patch("xmipp3_installer.repository.config.datetime") as mock_lib:
		mock_today = Mock()
		mock_today.strftime.return_value = file_content.DATE
		mock_lib.today.return_value = mock_today
		yield mock_lib
