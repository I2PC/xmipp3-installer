import os
import subprocess

import pytest

from xmipp3_installer.application.cli.arguments import modes
from xmipp3_installer.installer import constants
from xmipp3_installer.shared import file_operations

from .shell_command_outputs import mode_version
from .. import (
	get_assertion_message, copy_file_from_reference,
	get_test_file, create_versions_json_file, JSON_XMIPP_VERSION_NAME
)

def test_returns_short_version(__setup_evironment):
	command_words = ["xmipp3_installer", modes.MODE_VERSION, "--short"]
	result = subprocess.run(command_words, capture_output=True, text=True)
	expected_version = f"{JSON_XMIPP_VERSION_NAME}\n"
	assert (
		result.stdout == expected_version
	), get_assertion_message("short version", expected_version, result.stdout)

@pytest.mark.parametrize(
	"__setup_evironment,expected_output_function",
	[
		pytest.param((False, False), mode_version.get_full_info_before_config),
		pytest.param((False, True), mode_version.get_full_info_before_config_with_sources),
		pytest.param((True, False), mode_version.get_full_info_after_config_without_sources),
		pytest.param((True, True), mode_version.get_full_info_after_config_with_sources)
	],
	indirect=["__setup_evironment"]
)
def test_returns_full_version(
	__setup_evironment,
	expected_output_function
):
	command_words = ["xmipp3_installer", modes.MODE_VERSION]
	result = subprocess.run(command_words, capture_output=True, text=True)
	expected_output = expected_output_function()
	assert (
		result.stdout == expected_output
	), get_assertion_message("full version", expected_output, result.stdout)

def __delete_library_versions_file():
	file_operations.delete_paths(
		[os.path.dirname(constants.LIBRARY_VERSIONS_FILE)]
	)

@pytest.fixture(params=[(False, False)])
def __setup_evironment(request):
	config_done, sources_exist = request.param
	try:
		create_versions_json_file()
		if not config_done:
			__delete_library_versions_file()
			file_operations.delete_paths([constants.CONFIG_FILE])
		else:
			copy_file_from_reference(
				get_test_file("libraries-with-versions.txt"),
				constants.LIBRARY_VERSIONS_FILE
			)
			copy_file_from_reference(
				get_test_file(os.path.join("conf_files", "input", "default.conf")),
				constants.CONFIG_FILE
			)
		if not sources_exist:
			file_operations.delete_paths([constants.XMIPP_CORE_PATH])
		else:
			os.makedirs(constants.XMIPP_CORE_PATH, exist_ok=True)
		yield config_done, sources_exist
	finally:
		__delete_library_versions_file()
		file_operations.delete_paths([
			constants.CONFIG_FILE,
			constants.XMIPP_CORE_PATH,
			constants.VERSION_INFO_FILE
		])
