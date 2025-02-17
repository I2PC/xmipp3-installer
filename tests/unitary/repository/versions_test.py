import json
from io import StringIO
from unittest.mock import patch

import pytest

from xmipp3_installer.repository import versions

from ... import get_assertion_message

__UNICODE_DECODE_ERROR = UnicodeDecodeError("utf-8", b"", 0, 1, "Error")
__JSON_DECODE_ERROR = json.JSONDecodeError("Error", "doc", 0)
__LOADED_JSON = {"key": "value"}
__FILE_PATH = "/path/to/file.json"

def test_calls_json_load_when_reading_json_from_file_data(
	__get_json_file,
	__mock_json_load
):
	versions.__read_json_from_file_data(__get_json_file, False)
	__mock_json_load.assert_called_once_with(__get_json_file)

def test_calls_logger_if_json_file_has_invalid_encoding_and_show_warnings_enabled_when_reading_json_from_file_data(
	__get_json_file,
	__mock_json_load,
	__mock_logger,
	__mock_logger_yellow
):
	__mock_json_load.return_value = None
	__mock_json_load.side_effect = __UNICODE_DECODE_ERROR
	versions.__read_json_from_file_data(__get_json_file, True)
	__mock_logger.assert_called_once_with(
		__mock_logger_yellow(
			 f"WARNING: Version information is not encoded properly:\n{__UNICODE_DECODE_ERROR}"
		)
	)

def test_calls_logger_if_json_file_has_invalid_format_and_show_warnings_enabled_when_reading_json_from_file_data(
	__get_json_file,
	__mock_json_load,
	__mock_logger,
	__mock_logger_yellow
):
	__mock_json_load.return_value = None
	__mock_json_load.side_effect = __JSON_DECODE_ERROR
	versions.__read_json_from_file_data(__get_json_file, True)
	error_message = "WARNING: Version information is not in valid JSON format. "
	error_message += f"See complete error below:\n{__JSON_DECODE_ERROR}"
	__mock_logger.assert_called_once_with(
		__mock_logger_yellow(error_message)
	)

@pytest.mark.parametrize(
	"__mock_json_load",
	[pytest.param((True, False)), pytest.param((True, True))],
	indirect=["__mock_json_load"]
)
def test_does_not_call_logger_if_show_warnins_disabled_when_reading_json_from_file_data(
	__get_json_file,
	__mock_json_load,
	__mock_logger
):
	versions.__read_json_from_file_data(__get_json_file, False)
	__mock_logger.assert_not_called()

@pytest.mark.parametrize(
	"__mock_json_load,expected_json",
	[
		pytest.param((True, False), {}),
		pytest.param((True, True), {}),
		pytest.param((False, False), __LOADED_JSON),
		pytest.param((False, True), __LOADED_JSON)
	],
	indirect=["__mock_json_load"]
)
def test_returns_expected_json_from_file_data(
	__get_json_file,
	__mock_json_load,
	expected_json
):
	json_data = versions.__read_json_from_file_data(__get_json_file, False)
	assert (
		json_data == expected_json
	), get_assertion_message("loaded JSON data", expected_json, json_data)

def test_calls_os_path_exists_when_getting_version_info(
	__mock_os_path_exists
):
	__mock_os_path_exists.return_value = False
	versions.get_version_info(__FILE_PATH)
	__mock_os_path_exists.assert_called_once_with(__FILE_PATH)

def test_calls_open_when_getting_version_info(
	__mock_os_path_exists,
	__mock_open
):
	versions.get_version_info(__FILE_PATH)
	__mock_open.assert_called_once_with(__FILE_PATH)

@pytest.mark.parametrize(
	"__mock_os_path_exists,__mock_read_json_from_file_data,"
	"expected_json_data",
	[
		pytest.param(False, {}, {}),
		pytest.param(False, __LOADED_JSON, {}),
		pytest.param(True, {}, {}),
		pytest.param(True, __LOADED_JSON, __LOADED_JSON)
	],
	indirect=["__mock_os_path_exists", "__mock_read_json_from_file_data"]
)
def test_returns_expected_version_info(
	__mock_os_path_exists,
	__mock_read_json_from_file_data,
	expected_json_data,
	__mock_open
):
	json_data = versions.get_version_info(__FILE_PATH)
	assert (
		json_data == expected_json_data
	), get_assertion_message("JSON data", expected_json_data, json_data)

@pytest.fixture
def __get_json_file():
	json_file = StringIO()
	json.dump(__LOADED_JSON, json_file)
	return json_file

@pytest.fixture(params=[(False, False)])
def __mock_json_load(request):
	is_error, unicode_error = request.param
	with patch("json.load") as mock_method:
		if is_error:
			error = __UNICODE_DECODE_ERROR if unicode_error else __JSON_DECODE_ERROR
			mock_method.side_effect = error
		else:
			mock_method.return_value = __LOADED_JSON
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_logger():
	with patch(
		"xmipp3_installer.application.logger.logger.Logger.__call__"
	) as mock_method:
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_logger_yellow():
	with patch(
		"xmipp3_installer.application.logger.logger.Logger.yellow"
	) as mock_method:
		mock_method.side_effect = lambda text: f"yellow-{text}-yellow"
		yield mock_method

@pytest.fixture(params=[True])
def __mock_os_path_exists(request):
	with patch("os.path.exists") as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture
def __mock_open(__get_json_file):
	with patch("builtins.open") as mock_method:
		mock_method.return_value = __get_json_file
		yield mock_method

@pytest.fixture(params=[__LOADED_JSON])
def __mock_read_json_from_file_data(request):
	with patch(
		"xmipp3_installer.repository.versions.__read_json_from_file_data"
	) as mock_method:
		mock_method.return_value = request.param
		yield mock_method
