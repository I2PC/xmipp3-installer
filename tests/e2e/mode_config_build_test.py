import os
import subprocess

import pytest

from xmipp3_installer.application.cli.arguments import modes, params
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.shared import file_operations

from . import get_cmake_project_path
from .shell_command_outputs import mode_config_build
from .. import (
	create_versions_json_file, get_assertion_message,
	copy_file_from_reference, get_test_file
)

import sys
from io import StringIO
from unittest.mock import patch
from xmipp3_installer.application.cli import arguments, cli
@pytest.mark.parametrize(
	"__setup_evironment,expected_output",
	[
		pytest.param(False, mode_config_build.FAILURE, id="Failure"),
		pytest.param(True, mode_config_build.SUCCESS, id="Success")
	],
	indirect=["__setup_evironment"]
)
def test_returns_expected_config_build_output(
	__setup_evironment,
	expected_output,
	__mock_sys_argv,
	__mock_stdout_stderr
):
	stdout, _ = __mock_stdout_stderr
	cwd = os.getcwd()
	os.chdir(__setup_evironment)
	with pytest.raises(SystemExit):
		cli.main()
	os.chdir(cwd)
	stdout = __normalize_cmake_executable(stdout.getvalue())
	assert (
		stdout == expected_output
	), get_assertion_message("config build output", expected_output, stdout)
	#command_words = [
	#	"xmipp3_installer",
	#	modes.MODE_CONFIG_BUILD,
	#	params.PARAMS[params.PARAM_KEEP_OUTPUT][params.LONG_VERSION]
	#]
	#result = subprocess.run(
	#	command_words, capture_output=True, text=True, cwd=__setup_evironment
	#)
	#result = __normalize_cmake_executable(result.stdout)
	#assert (
	#	result == expected_output
	#), get_assertion_message("config build output", expected_output, result)

def __normalize_cmake_executable(raw_output: str) -> str:
	first_flag_index = raw_output.find(" -S")
	text_up_to_cmake_exec = raw_output[:first_flag_index]
	splitted_first_lines = text_up_to_cmake_exec.split("\n")
	return "\n".join([splitted_first_lines[0], mode_config_build.CMAKE_EXECUTABLE]) + raw_output[first_flag_index:]

@pytest.fixture(params=[True])
def __setup_evironment(request):
	cmake_project_name = "valid" if request.param else "config_error"
	project_path = get_cmake_project_path(cmake_project_name)
	try:
		create_versions_json_file(output_path=project_path)
		copy_file_from_reference(
			get_test_file(os.path.join("conf-files", "input", "all-off.conf")),
			os.path.join(project_path, paths.CONFIG_FILE)
		)
		yield get_cmake_project_path(cmake_project_name)
	finally:
		file_operations.delete_paths([
			os.path.join(project_path, file_name) for file_name in [
				paths.VERSION_INFO_FILE,
				paths.BUILD_PATH,
				paths.CONFIG_FILE,
				paths.LOG_FILE
			]
		])

@pytest.fixture(autouse=True)
def __mock_sys_argv():
	args = [
		arguments.XMIPP_PROGRAM_NAME,
		modes.MODE_CONFIG_BUILD,
		params.PARAMS[params.PARAM_KEEP_OUTPUT][params.LONG_VERSION]
	]
	with patch.object(sys, 'argv', args) as mock_object:
		yield mock_object

@pytest.fixture
def __mock_stdout_stderr():
	new_stdout, new_stderr = StringIO(), StringIO()
	with patch('sys.stdout', new=new_stdout), patch('sys.stderr', new=new_stderr):
		yield new_stdout, new_stderr
