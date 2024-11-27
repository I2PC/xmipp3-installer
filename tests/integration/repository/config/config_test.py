import os
import tempfile
from unittest.mock import patch, Mock

import pytest

from xmipp3_installer.repository.config import ConfigurationFileHandler

from . import file_content
from .... import get_assertion_message

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
		"config file content",
		file_content.DEFAULT_FILE_LINES,
		config_file_content
	)

def test_writes_unkown_variables_to_config_when_unkown_variables_are_added_to_values(
	__mock_config_file,
	__mock_datetime_strftime
):
	config_handler = ConfigurationFileHandler(__mock_config_file.name)
	config_handler.values.update({"UNKNOWN": "myvalue"})
	config_handler.write_config()
	config_file_content = ''.join(
		config_handler._ConfigurationFileHandler__get_file_content()
	).split("\n")
	expected_file_content = [
		*file_content.TOGGLE_SECTION_LINES,
		*file_content.PACKAGE_HOME_SECTION_LINES,
		*file_content.COMPILATION_FLAGS_SECTION_LINES,
		*file_content.UNKNOWN_VARIABLES_HEADER,
		"UNKNOWN=myvalue",
		"",
		*file_content.LAST_MODIFIED_LINES
	]
	assert (
		config_file_content == expected_file_content
	), get_assertion_message(
		"config file content",
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
