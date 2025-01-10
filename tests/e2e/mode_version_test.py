import subprocess

from xmipp3_installer.api_client.assembler import installation_info_assembler
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer.tmp import versions
from xmipp3_installer.installer.handlers import git_handler

from .. import get_assertion_message

__TITLE = f"Xmipp {versions.XMIPP_VERSIONS[versions.XMIPP][versions.VERSION_KEY]} ({git_handler.get_current_branch()})"
__SOURCE_NOT_FOUND_MESSAGE = logger.yellow("Not found")
__FULL_INFO_BEFORE_CONFIG = f"""{logger.bold(__TITLE)}

Release date:            {versions.RELEASE_DATE}
Compilation date:        -
System version:          {installation_info_assembler.get_os_release_name()}
xmippCore branch:        {__SOURCE_NOT_FOUND_MESSAGE}
xmippViz branch:         {__SOURCE_NOT_FOUND_MESSAGE}
scipion-em-xmipp branch: {__SOURCE_NOT_FOUND_MESSAGE}
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
