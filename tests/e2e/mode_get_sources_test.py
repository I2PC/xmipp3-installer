import os
import sys
from io import StringIO
from unittest.mock import patch

import pytest

from xmipp3_installer.application.cli import cli
from xmipp3_installer.application.cli import arguments
from xmipp3_installer.application.cli.arguments import modes, params
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.installer.handlers import shell_handler
from xmipp3_installer.shared import file_operations

from .shell_command_outputs import mode_get_sources
from .. import get_assertion_message, create_versions_json_file

@pytest.mark.parametrize(
	"__mock_sys_argv,__mock_clone_and_checkout,"
	"__setup_evironment,expected_output",
	[
		pytest.param(
			[],
			(0, ""),
			False,
			mode_get_sources.SUCCESS,
			id="Clone success main branch"
		),
		pytest.param(
			[],
			(0, ""),
			True,
			mode_get_sources.SUCCESS,
			id="Skip checkout 1"
		),
		pytest.param(
			[],
			(1, mode_get_sources.GIT_COMMAND_FAILURE_MESSAGE),
			False,
			mode_get_sources.FAILURE,
			id="Clone failure main branch"
		),
		pytest.param(
			[],
			(1, mode_get_sources.GIT_COMMAND_FAILURE_MESSAGE),
			True,
			mode_get_sources.SUCCESS,
			id="Skip checkout 2"
		),
		pytest.param(
			[
				params.PARAMS[params.PARAM_BRANCH][params.SHORT_VERSION],
				mode_get_sources.BRANCH_NAME
			],
			(0, ""),
			False,
			mode_get_sources.SUCCESS_WITH_WARNING,
			id="Clone success non-existing different branch"
		),
		pytest.param(
			[
				params.PARAMS[params.PARAM_BRANCH][params.SHORT_VERSION],
				mode_get_sources.BRANCH_NAME
			],
			(0, f"refs/heads/{mode_get_sources.BRANCH_NAME}"),
			False,
			mode_get_sources.SUCCESS,
			id="Clone success existing different branch"
		),
		pytest.param(
			[
				params.PARAMS[params.PARAM_BRANCH][params.SHORT_VERSION],
				mode_get_sources.BRANCH_NAME
			],
			(1, mode_get_sources.GIT_COMMAND_FAILURE_MESSAGE),
			False,
			mode_get_sources.FAILURE_WITH_WARNING,
			id="Clone failure non-existing different branch"
		),
		pytest.param(
			[
				params.PARAMS[params.PARAM_BRANCH][params.SHORT_VERSION],
				mode_get_sources.BRANCH_NAME
			],
			(1, mode_get_sources.GIT_COMMAND_FAILURE_MESSAGE),
			True,
			mode_get_sources.SUCCESS_WITH_WARNING,
			id="Skip checkout with non-existing branch"
		),
	],
	indirect=[
		"__mock_sys_argv",
		"__mock_clone_and_checkout",
		"__setup_evironment"
	]
)
def test_returns_returns_expected_get_sources_output(
	__setup_evironment,
	expected_output,
	__mock_stdout_stderr,
	__mock_clone_and_checkout
):
	stdout, _ = __mock_stdout_stderr
	with pytest.raises(SystemExit):
		cli.main()
	output = stdout.getvalue()
	assert (
		output == expected_output
	), get_assertion_message("get sources command output", expected_output, output)

@pytest.fixture(params=[False])
def __setup_evironment(request):
	sources_exist = request.param
	try:
		create_versions_json_file()
		if not sources_exist:
			file_operations.delete_paths(paths.XMIPP_SOURCE_PATHS)
		else:
			for source in paths.XMIPP_SOURCE_PATHS:
				os.makedirs(source, exist_ok=True)
		yield sources_exist
	finally:
		file_operations.delete_paths([
			*paths.XMIPP_SOURCE_PATHS,
			paths.VERSION_INFO_FILE
		])

@pytest.fixture(autouse=True, params=[[]])
def __mock_sys_argv(request):
	params = [
		arguments.XMIPP_PROGRAM_NAME,
		modes.MODE_GET_SOURCES,
		*request.param
	]
	with patch.object(sys, 'argv', params) as mock_object:
		yield mock_object

@pytest.fixture
def __mock_stdout_stderr():
	new_stdout, new_stderr = StringIO(), StringIO()
	with patch('sys.stdout', new=new_stdout), patch('sys.stderr', new=new_stderr):
		yield new_stdout, new_stderr

@pytest.fixture(params=[(0, "")])
def __mock_clone_and_checkout(request, __mock_sys_argv):
	original_run_shell_command = shell_handler.run_shell_command
	def __side_effect(cmd: str, **kwargs):
		if (
			cmd.startswith("git clone") or
			cmd.startswith("git checkout") or
			(
				(
					params.PARAMS[params.PARAM_BRANCH][params.SHORT_VERSION] in __mock_sys_argv or
					params.PARAMS[params.PARAM_BRANCH][params.LONG_VERSION] in __mock_sys_argv
				) and
				cmd.startswith("git ls-remote")
			)
		):
			return request.param
		return original_run_shell_command(cmd, **kwargs)
	with patch(
		"xmipp3_installer.installer.handlers.shell_handler.run_shell_command"
	) as mock_method:
		mock_method.side_effect = __side_effect
		yield mock_method
