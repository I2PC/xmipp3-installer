import os
import shutil
import subprocess

import pytest

from xmipp3_installer.installer import constants
from xmipp3_installer.installer.tmp import versions

from .shell_command_outputs import mode_version
from .. import get_assertion_message

def test_returns_short_version():
	command_words = ["xmipp3_installer", "version", "--short"]
	result = subprocess.run(command_words, capture_output=True, text=True)
	expected_version = f"{versions.XMIPP_VERSIONS[versions.XMIPP][versions.VERNAME_KEY]}\n"
	assert (
		result.stdout == expected_version
	), get_assertion_message("short version", expected_version, result.stdout)

@pytest.mark.parametrize(
	"__setup_config_evironment,expected_output",
	[
		pytest.param(False, mode_version.FULL_INFO_BEFORE_CONFIG),
		pytest.param(True, mode_version.FULL_INFO_AFTER_CONFIG_NO_SOURCES)
	],
	indirect=["__setup_config_evironment"]
)
def test_returns_full_version_with_no_sources(
	__setup_config_evironment,
	expected_output
):
	command_words = ["xmipp3_installer", "version"]
	result = subprocess.run(command_words, capture_output=True, text=True)
	assert (
		result.stdout == expected_output
	), get_assertion_message("full version", expected_output, result.stdout)

def __get_test_library_versions_file():
	return os.path.join(
		os.path.dirname(os.path.abspath(__file__)),
		"test_files",
		"libraries-with-versions.txt"
	)

def __delete_library_versions_file():
	file_directory = os.path.dirname(constants.LIBRARY_VERSIONS_FILE)
	if os.path.exists(file_directory):
		shutil.rmtree(file_directory)

def __copy_file_from_reference():
	file_directory = os.path.dirname(constants.LIBRARY_VERSIONS_FILE)
	if not os.path.exists(file_directory):
		os.makedirs(file_directory)
	shutil.copyfile(
		__get_test_library_versions_file(),
		constants.LIBRARY_VERSIONS_FILE
	)

@pytest.fixture(params=[False])
def __setup_config_evironment(request):
	try:
		if not request.param:
			__delete_library_versions_file()
		else:
			__copy_file_from_reference()
		yield request.param
	finally:
		__delete_library_versions_file()
