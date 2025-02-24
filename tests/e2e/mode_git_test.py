import os
import subprocess

import pytest

from xmipp3_installer.application.cli.arguments import modes
from xmipp3_installer.installer import constants
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.shared import file_operations

from .shell_command_outputs import mode_git
from .. import get_assertion_message, create_versions_json_file

__XMIPP_PATH = paths.get_source_path(constants.XMIPP)

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
def test_returns_returns_expected_git_command_output(
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
		create_versions_json_file()
		if not xmipp_exists:
			file_operations.delete_paths([__XMIPP_PATH])
		else:
			os.makedirs(__XMIPP_PATH, exist_ok=True)
		if not xmipp_core_exists:
			file_operations.delete_paths(
				[paths.get_source_path(constants.XMIPP_CORE)]
			)
		else:
			os.makedirs(paths.get_source_path(constants.XMIPP_CORE), exist_ok=True)
		yield xmipp_exists, xmipp_core_exists
	finally:
		file_operations.delete_paths([
			__XMIPP_PATH,
			paths.get_source_path(constants.XMIPP_CORE),
			constants.VERSION_INFO_FILE
		])
