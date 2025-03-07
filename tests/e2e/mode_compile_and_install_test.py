import os
import shutil
import subprocess

import pytest

from xmipp3_installer.application.cli.arguments import modes, params
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.shared import file_operations

from . import get_cmake_project_path
from .shell_command_outputs import mode_cmake
from .shell_command_outputs.mode_cmake import mode_compile_and_install
from .. import (
	create_versions_json_file, get_assertion_message,
	copy_file_from_reference
)

@pytest.mark.parametrize(
	"__setup_evironment,expected_output",
	[
		pytest.param((False, False), mode_compile_and_install.BUILD_FAILURE, id="All fail"),
		pytest.param((False, True), mode_compile_and_install.BUILD_FAILURE, id="Build error"),
		pytest.param((True, False), mode_compile_and_install.INSTALL_FAILURE, id="Install error"),
		pytest.param((True, True), mode_compile_and_install.SUCCESS, id="Success")
	],
	indirect=["__setup_evironment"]
)
def test_returns_expected_compile_and_install_output(
	__setup_evironment,
	expected_output
):
	command_words = [
		"xmipp3_installer",
		modes.MODE_COMPILE_AND_INSTALL,
		params.PARAMS[params.PARAM_KEEP_OUTPUT][params.LONG_VERSION],
		params.PARAMS[params.PARAM_JOBS][params.SHORT_VERSION],
		"1"
	]
	subprocess.run(
		["cmake", ".", "-B", f"{paths.BUILD_PATH}/"],
		cwd=__setup_evironment,
		env=mode_cmake.ENV,
		stdout=subprocess.PIPE
	)
	result = subprocess.run(
		command_words,
		capture_output=True,
		text=True,
		cwd=__setup_evironment,
		env=mode_cmake.ENV
	).stdout
	result = __normalize_line_breaks(
		__remove_detailed_command_error_line(
			__normalize_error_path(
				__setup_evironment,
				__remove_ninja_output(
					__normalize_cmake_executable(result)
				)
			)
		)
	)
	assert (
		result == expected_output
	), get_assertion_message("compile and install output", expected_output, result)

def __normalize_cmake_executable(raw_output: str) -> str: # CMake used deppends on user's installation
	return raw_output.replace(shutil.which("cmake"), mode_cmake.CMAKE_EXECUTABLE)

def __normalize_error_path(project_path: str, raw_output: str) -> str: # Absolute path changes per user and OS
	path_index = raw_output.find(mode_compile_and_install.ERROR_TARGET_MESSAGE_START)
	if path_index == -1:
		return raw_output
	path_index += len(mode_compile_and_install.ERROR_TARGET_MESSAGE_START)
	text_up_to_path = raw_output[:path_index]
	next_line_index = raw_output.find("\n", path_index)
	build_error_target_path = os.path.join(
		project_path,
		mode_compile_and_install.BUILD_ERROR_TARGET_SUBPATH
	)
	return f"{text_up_to_path}{build_error_target_path}{raw_output[next_line_index:]}"

def __remove_detailed_command_error_line(raw_output: str) -> str: # Error line containing system-specific details
	splitted = raw_output.splitlines(keepends=True)
	new_output_lines = []
	for line in splitted:
		if "cd " in line: # It's the only line containig a directory change
			continue
		new_output_lines.append(line)
	return ''.join(new_output_lines)

def __normalize_line_breaks(raw_output: str) -> str: # The number of line breaks in CMake is OS dependant
	splitted = raw_output.splitlines()
	previous_line = None
	new_lines = []
	for line in splitted:
		if not line:
			previous_line = line
			continue
		if (
			line == mode_compile_and_install.INSTALLING_MESSAGE_LINE or
			(line.startswith("**") and previous_line == "")
		):
			line = f"\n{line}"
		previous_line = line
		new_lines.append(line)
	return "\n".join([*new_lines, ""])

def __remove_ninja_output(raw_output: str) -> str: # Ninja output is printed or not depending on OS
	new_lines = []
	for line in raw_output.splitlines(keepends=True):
		line_without_ends = line.replace("\n", "").replace("\r", "")
		if line_without_ends in mode_compile_and_install.NINJA_OUTPUTS:
			continue
		new_lines.append(line)
	return "".join(new_lines)

@pytest.fixture(params=[(True, True)])
def __setup_evironment(request):
	build, install = request.param
	if not build:
		cmake_project_name = mode_cmake.BUILD_ERROR_PROJECT
	elif not install:
		cmake_project_name = mode_cmake.INSTALL_ERROR_PROJECT
	else:
		cmake_project_name = mode_cmake.VALID_PROJECT
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
