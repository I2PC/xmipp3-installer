import os
import subprocess

import pytest

from xmipp3_installer.application.cli.arguments import modes
from xmipp3_installer.installer import constants
from xmipp3_installer.repository import file_operations

from .shell_command_outputs import mode_git
from .. import get_assertion_message

__XMIPP_PATH = os.path.join(constants.SOURCES_PATH, constants.XMIPP)

@pytest.mark.parametrize(
	"__setup_evironment,expected_output_function",
	[
		pytest.param((False, False), mode_git.get_git_command_no_xmipp_no_xmipp_core),
		pytest.param((False, True), mode_git.get_git_command_no_xmipp_with_xmipp_core),
		pytest.param((True, False), mode_git.get_git_command_with_xmipp_no_xmipp_core),
		pytest.param((True, True), mode_git.get_git_command_with_xmipp_with_xmipp_core)
	],
	indirect=["__setup_evironment"]
)
def test_returns_full_version(
	__setup_evironment,
	expected_output_function
):
	command_words = ["xmipp3_installer", modes.MODE_GIT, "branch"]
	result = subprocess.run(command_words, capture_output=True, text=True)
	expected_output = expected_output_function()
	assert (
		result.stdout == expected_output
	), get_assertion_message("git command output", expected_output, result.stdout)

@pytest.fixture(params=[False, False])
def __setup_evironment(request):
	xmipp_exists, xmipp_core_exists = request.param
	try:
		if not xmipp_exists:
			file_operations.delete_paths([__XMIPP_PATH])
		else:
			os.makedirs(__XMIPP_PATH, exist_ok=True)
		if not xmipp_core_exists:
			file_operations.delete_paths([constants.XMIPP_CORE_PATH])
		else:
			os.makedirs(constants.XMIPP_CORE_PATH, exist_ok=True)
		yield xmipp_exists, xmipp_core_exists
	finally:
		file_operations.delete_paths([__XMIPP_PATH, constants.XMIPP_CORE_PATH])
