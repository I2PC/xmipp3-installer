import os
import re
import subprocess

import pytest

from xmipp3_installer.application.cli.arguments import modes, params
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.shared import file_operations

from . import get_cmake_project_path
from .shell_command_outputs import mode_cmake
from .shell_command_outputs.mode_cmake import mode_config_build
from .. import (
	create_versions_json_file, get_assertion_message,
	copy_file_from_reference
)

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
	expected_output
):
	command_words = [
		"xmipp3_installer",
		modes.MODE_CONFIG_BUILD,
		params.PARAMS[params.PARAM_KEEP_OUTPUT][params.LONG_VERSION]
	]
	result = subprocess.run(
		command_words,
		capture_output=True,
		text=True,
		cwd=__setup_evironment,
		env=mode_cmake.ENV
	)
	result = __normalize_paths(
		__normalize_execution_times(
			__normalize_generator_line(
				__normalize_cmake_executable(result.stdout)
			)
		)
	)
	assert (
		result == expected_output
	), get_assertion_message("config build output", expected_output, result)

def __normalize_cmake_executable(raw_output: str) -> str: # CMake used deppends on user's installation
	first_flag_index = raw_output.find(" -S")
	text_up_to_cmake_exec = raw_output[:first_flag_index]
	splitted_first_lines = text_up_to_cmake_exec.splitlines()
	return "\n".join([splitted_first_lines[0], mode_cmake.CMAKE_EXECUTABLE]) + raw_output[first_flag_index:]

def __normalize_generator_line(raw_output: str) -> str: # Generator used is sometimes printed, others not
	return raw_output.replace(mode_config_build.GENERATOR_LINE, "")

def __normalize_execution_times(raw_output: str) -> str: # Execution times vary from one execution to another
	return re.sub(r'\(\d+\.\ds\)', f"({mode_config_build.EXECUTION_TIME}s)", raw_output)

def __normalize_paths(raw_output: str) -> str: # Absolute paths are different per user and OS
	raw_output_lines = raw_output.splitlines(keepends=True)
	new_lines = []
	for line in raw_output_lines:
		if line.startswith(mode_config_build.BUILD_FILES_WRITTEN_MESSAGE_START):
			line = f"{mode_config_build.BUILD_FILES_WRITTEN_MESSAGE_START}{mode_config_build.VALID_PATH}\n"
		new_lines.append(line)
	return "".join(new_lines)

@pytest.fixture(params=[True])
def __setup_evironment(request):
	cmake_project_name = mode_cmake.VALID_PROJECT if request.param else mode_cmake.CONFIG_ERROR_PROJECT
	project_path = get_cmake_project_path(cmake_project_name)
	try:
		create_versions_json_file(output_path=project_path)
		copy_file_from_reference(
			mode_cmake.TEST_CONFIG_FILE_PATH,
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
