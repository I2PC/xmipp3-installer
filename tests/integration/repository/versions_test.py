import os
from io import StringIO
from unittest.mock import patch

import pytest

from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer import constants
from xmipp3_installer.repository import versions
from xmipp3_installer.shared import file_operations

from ... import copy_file_from_reference, get_test_file, get_assertion_message

__JSON_INFO = {
	constants.XMIPP: {
		versions.VERSION_NUMBER_KEY: "3.X.Y",
		versions.VERSION_NAME_KEY: "v3.X.Y-TBD",
		versions.RELEASE_DATE_KEY: "dd/mm/yyyy"
	},
	versions.SOURCES_KEY: {
		constants.XMIPP_CORE: {
			versions.MIN_VERSION_KEY: "3.25.0"
		}
	}
}
__INVALID_FORMAT_WARNING_MESSAGE = logger.yellow("""WARNING: Version information is not in valid JSON format. See complete error below:
Expecting property name enclosed in double quotes: line 6 column 5 (char 117)""") + "\n"

@pytest.mark.parametrize(
	"__setup_environment,expected_info,expected_output_message",
	[
		pytest.param((False, "valid"), {}, ""),
		pytest.param((False, "syntax-error"), {}, ""),
		pytest.param((True, "valid"), __JSON_INFO, ""),
		pytest.param((True, "syntax-error"), {}, __INVALID_FORMAT_WARNING_MESSAGE)
	],
	indirect=["__setup_environment"]
)
def test_returns_expected_version_information(
	__setup_environment,
	expected_info,
	expected_output_message,
	__mock_stdout_stderr
):
	stdout, _ = __mock_stdout_stderr
	version_info = versions.get_version_info(constants.VERSION_INFO_FILE)
	stdout_value = stdout.getvalue()
	assert (
		version_info == expected_info
	), get_assertion_message(
		"version information",
		expected_info,
		version_info
	)
	assert (
		stdout_value == expected_output_message
	), get_assertion_message(
		"output message",
		expected_output_message,
		stdout_value
	)

@pytest.fixture(params=[False, "valid"])
def __setup_environment(request):
	file_exists, file_name = request.param
	try:
		if file_exists:
			copy_file_from_reference(
				get_test_file(
					os.path.join(
						"version_info_files",
						f"{file_name}.json"
					)
				),
				constants.VERSION_INFO_FILE
			)
		else:
			file_operations.delete_paths([
				constants.VERSION_INFO_FILE
			])
		yield
	finally:
		file_operations.delete_paths([
			constants.VERSION_INFO_FILE
		])

@pytest.fixture
def __mock_stdout_stderr():
	new_stdout, new_stderr = StringIO(), StringIO()
	with patch('sys.stdout', new=new_stdout), patch('sys.stderr', new=new_stderr):
		yield new_stdout, new_stderr
