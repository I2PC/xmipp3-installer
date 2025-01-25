import os
import subprocess

import pytest

from xmipp3_installer.installer import constants
from xmipp3_installer.installer.tmp import versions
from xmipp3_installer.repository import file_operations

from .shell_command_outputs import mode_version
from .. import (
	get_assertion_message, copy_file_from_reference, get_test_file
)

def test_returns_short_version():
	command_words = ["xmipp3_installer", "version", "--short"]
	result = subprocess.run(command_words, capture_output=True, text=True)
	expected_version = f"{versions.XMIPP_VERSIONS[versions.XMIPP][versions.VERNAME_KEY]}\n"
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
	command_words = ["xmipp3_installer", "version"]
	result = subprocess.run(command_words, capture_output=True, text=True)
	expected_output = expected_output_function()
	assert (
		result.stdout == expected_output
	), get_assertion_message("full version", expected_output, result.stdout)

def __delete_library_versions_file():
	file_operations.delete_paths(
		[os.path.dirname(constants.LIBRARY_VERSIONS_FILE)]
	)

def __delete_sources():
	file_operations.delete_paths([
		os.path.join(constants.SOURCES_PATH, source)
		for source in constants.XMIPP_SOURCES
	])

def __make_source_directories():
	for source in constants.XMIPP_SOURCES:
		source_path = os.path.join(constants.SOURCES_PATH, source)
		os.makedirs(source_path, exist_ok=True)

@pytest.fixture(params=[False, False])
def __setup_evironment(request):
	lib_file_exist, sources_exist = request.param
	try:
		if not lib_file_exist:
			__delete_library_versions_file()
		else:
			copy_file_from_reference(
				get_test_file("libraries-with-versions.txt"),
				constants.LIBRARY_VERSIONS_FILE
			)
		if not sources_exist:
			__delete_sources()
		else:
			__make_source_directories()
		yield lib_file_exist, sources_exist
	finally:
		__delete_library_versions_file()
		__delete_sources()
