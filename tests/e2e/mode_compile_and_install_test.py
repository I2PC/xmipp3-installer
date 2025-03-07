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
	result = mode_compile_and_install.normalize_line_breaks(
		mode_compile_and_install.remove_command_error_line(
			mode_compile_and_install.normalize_error_path(
				__setup_evironment,
				mode_compile_and_install.remove_ninja_output(
					mode_cmake.normalize_cmake_executable(result)
				)
			)
		)
	)
	assert (
		result == expected_output
	), get_assertion_message("compile and install output", expected_output, result)

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
		yield project_path
	finally:
		file_operations.delete_paths([
			os.path.join(project_path, file_name) for file_name in [
				paths.VERSION_INFO_FILE,
				paths.BUILD_PATH,
				paths.CONFIG_FILE,
				paths.LOG_FILE
			]
		])
