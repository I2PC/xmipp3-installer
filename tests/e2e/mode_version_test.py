import os
import shutil
import subprocess

import pytest

from xmipp3_installer.api_client.assembler import installation_info_assembler
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer import constants
from xmipp3_installer.installer.tmp import versions
from xmipp3_installer.installer.handlers import git_handler

from .. import get_assertion_message

__TITLE = f"Xmipp {versions.XMIPP_VERSIONS[versions.XMIPP][versions.VERSION_KEY]} ({git_handler.get_current_branch()})"
__SOURCE_NOT_FOUND_MESSAGE = logger.yellow("Not found")
__WARNING_MESSAGE = f"""{logger.yellow("This project has not yet been configured, so some detectable dependencies have not been properly detected.")}
{logger.yellow("Run mode 'getSources' and then 'configBuild' to be able to show all detectable ones.")}"""
__LIBRARIES_WITH_VERSIONS = """CMake:                   3.31.3
CC:                      GNU-13.3.0
CXX:                     GNU-13-3-0
Python3:                 3.12.8
MPI:                     3.1
HDF5:                    1.10.10
JPEG:                    80
SQLite3:                 3.45.1
Java:                    17.0.13
"""
__COMMON_SECTION = f"""{logger.bold(__TITLE)}

Release date:            {versions.RELEASE_DATE}
Compilation date:        -
System version:          {installation_info_assembler.get_os_release_name()}"""
__SOURCES_NOT_FOUND_SECTION = f"""xmippCore branch:        {__SOURCE_NOT_FOUND_MESSAGE}
xmippViz branch:         {__SOURCE_NOT_FOUND_MESSAGE}
scipion-em-xmipp branch: {__SOURCE_NOT_FOUND_MESSAGE}"""
__FULL_INFO_BEFORE_CONFIG = f"""{__COMMON_SECTION}
{__SOURCES_NOT_FOUND_SECTION}

{__WARNING_MESSAGE}
"""
__FULL_INFO_AFTER_CONFIG_NO_SOURCES = f"""{__COMMON_SECTION}
{__SOURCES_NOT_FOUND_SECTION}

{__LIBRARIES_WITH_VERSIONS}
{__WARNING_MESSAGE}
"""

def test_returns_short_version():
	command_words = ["xmipp3_installer", "version", "--short"]
	result = subprocess.run(command_words, capture_output=True, text=True)
	expected_version = f"{versions.XMIPP_VERSIONS[versions.XMIPP][versions.VERNAME_KEY]}\n"
	assert (
		result.stdout == expected_version
	), get_assertion_message("short version", expected_version, result.stdout)

def test_returns_full_version_before_config():
	command_words = ["xmipp3_installer", "version"]
	result = subprocess.run(command_words, capture_output=True, text=True)
	assert (
		result.stdout == __FULL_INFO_BEFORE_CONFIG
	), get_assertion_message("full version", __FULL_INFO_BEFORE_CONFIG, result.stdout)

@pytest.mark.parametrize(
	"__setup_config_evironment",
	[
		pytest.param(True)
	],
	indirect=["__setup_config_evironment"]
)
def test_returns_full_version_after_config_with_no_sources(
	__setup_config_evironment
):
	command_words = ["xmipp3_installer", "version"]
	result = subprocess.run(command_words, capture_output=True, text=True)
	assert (
		result.stdout == __FULL_INFO_AFTER_CONFIG_NO_SOURCES
	), get_assertion_message("full version", __FULL_INFO_AFTER_CONFIG_NO_SOURCES, result.stdout)

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
