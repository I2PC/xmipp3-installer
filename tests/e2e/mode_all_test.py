import os
import subprocess

import pytest

from xmipp3_installer.application.cli.arguments import modes, params
from xmipp3_installer.installer import constants
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.shared import file_operations

from . import get_cmake_project_path
from .shell_command_outputs import mode_cmake, mode_all
from .shell_command_outputs.mode_cmake import mode_config_build, mode_compile_and_install
from .. import (
	create_versions_json_file, get_assertion_message,
	copy_file_from_reference
)

@pytest.mark.parametrize(
	"__setup_evironment,expected_output",
	[
		pytest.param((False, False, False), mode_all.CONFIG_BUILD_FAILURE, id="All fail"),
		pytest.param((False, True, True), mode_all.CONFIG_BUILD_FAILURE, id="Build config error"),
		pytest.param((True, False, True), mode_all.BUILD_FAILURE, id="Build error"),
	],
	indirect=["__setup_evironment"]
)
def test_returns_expected_full_installation_output(
	__setup_evironment,
	expected_output
):
	command_words = [
		"xmipp3_installer",
		modes.MODE_ALL,
		params.PARAMS[params.PARAM_KEEP_OUTPUT][params.LONG_VERSION],
		params.PARAMS[params.PARAM_JOBS][params.SHORT_VERSION],
		"1"
	]
	result = subprocess.run(
		command_words,
		capture_output=True,
		text=True,
		cwd=__setup_evironment,
		env=mode_cmake.ENV
	).stdout
	result = mode_compile_and_install.remove_ninja_output(
		mode_config_build.normalize_execution_times(
			mode_config_build.remove_generator_line(
				mode_cmake.normalize_cmake_executable(result)
			)
		)
	)
	test = ""
	#result = __normalize_line_breaks(
	#	__remove_detailed_command_error_line(
	#		__normalize_error_path(
	#			__setup_evironment,
	#     result
	#		)
	#	)
	#)
	assert (
		result == expected_output
	), get_assertion_message("full installation output", expected_output, result)

@pytest.fixture(params=[(True, True, True)])
def __setup_evironment(request):
	configure, build, install = request.param
	if not configure:
		cmake_project_name = mode_cmake.CONFIG_ERROR_PROJECT
	elif not build:
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
		src_path = os.path.join(project_path, paths.SOURCES_PATH)
		os.makedirs(src_path, exist_ok=True)
		for source in constants.XMIPP_SOURCES:
			os.makedirs(os.path.join(src_path, source), exist_ok=True)
		yield get_cmake_project_path(cmake_project_name)
	finally:
		file_operations.delete_paths([
			os.path.join(project_path, file_name) for file_name in [
				paths.VERSION_INFO_FILE,
				paths.BUILD_PATH,
				paths.CONFIG_FILE,
				paths.LOG_FILE,
				paths.SOURCES_PATH
			]
		])
