import os
import sys
from io import StringIO
from unittest.mock import patch

import pytest

from xmipp3_installer.application.cli import cli
from xmipp3_installer.application.cli import arguments
from xmipp3_installer.application.cli.arguments import modes
from xmipp3_installer.installer.modes import mode_add_model_executor

from .shell_command_outputs import mode_add_model
from .. import copy_file_from_reference, delete_paths, get_assertion_message

__SYNC_PROGRAM_ROOT = "dist"
__MODEL_PATH = f"./tests/e2e/test_files/{mode_add_model.MODEL_NAME}"

@pytest.mark.parametrize(
	"__mock_sys_argv,__setup_evironment,update,"
	"__mock_sys_stdin,expected_message",
	[
		pytest.param(mode_add_model.NON_EXISTING_MODEL_PATH, False, False, False, mode_add_model.NO_MODEL),
		pytest.param(mode_add_model.NON_EXISTING_MODEL_PATH, True, True, True, mode_add_model.NO_MODEL),
		pytest.param(__MODEL_PATH, False, False, False, mode_add_model.NO_PROGRAM),
		pytest.param(__MODEL_PATH, False, True, True, mode_add_model.NO_PROGRAM),
		pytest.param(__MODEL_PATH, True, False, False, mode_add_model.CANCELLED),
		pytest.param(__MODEL_PATH, True, True, False, mode_add_model.CANCELLED),
		pytest.param(__MODEL_PATH, True, False, True, mode_add_model.UPLOADED),
		pytest.param(__MODEL_PATH, True, True, True, mode_add_model.UPLOADED)
	],
	indirect=["__mock_sys_argv", "__setup_evironment", "__mock_sys_stdin"]
)
def test_add_model(
	__mock_sys_argv,
	__setup_evironment,
	update,
	__mock_sys_stdin,
	expected_message,
	__mock_stdout_stderr
):
	stdout, _ = __mock_stdout_stderr
	if update:
		__mock_sys_argv.append("--update")
	with pytest.raises(SystemExit):
		cli.main()
	output = stdout.getvalue()
	assert (
		output == expected_message
	), get_assertion_message("add model output", expected_message, output)

def __get_sync_program_root():
	path_components = os.path.normpath(mode_add_model_executor._SYNC_PROGRAM_PATH).split(os.sep)
	root_index = path_components.index(__SYNC_PROGRAM_ROOT)
	root_components = path_components[:root_index + 1]
	return os.path.join(*root_components)

def __get_executable_file(name):
	return os.path.join(
		os.path.dirname(os.path.abspath(__file__)),
		"test_files",
		name
	)

@pytest.fixture(params=[False])
def __setup_evironment(request, __mock_sync_program_name):
	is_compiled = request.param
	sync_program_root = __get_sync_program_root()
	try:
		if not is_compiled:
			delete_paths([sync_program_root])
		else:
			copy_file_from_reference(
				__get_executable_file(__mock_sync_program_name),
				os.path.join(
					mode_add_model_executor._SYNC_PROGRAM_PATH,
					mode_add_model_executor._SYNC_PROGRAM_NAME
				)
			)
		yield is_compiled
	finally:
		delete_paths([sync_program_root])

@pytest.fixture(autouse=True, params=[__MODEL_PATH])
def __mock_sys_argv(request):
	params = [
		arguments.XMIPP_PROGRAM_NAME,
		modes.MODE_ADD_MODEL,
		mode_add_model.LOGIN,
		request.param
	]
	with patch.object(sys, 'argv', params) as mock_object:
		yield mock_object

@pytest.fixture
def __mock_stdout_stderr():
	new_stdout, new_stderr = StringIO(), StringIO()
	with patch('sys.stdout', new=new_stdout), patch('sys.stderr', new=new_stderr):
		yield new_stdout, new_stderr

@pytest.fixture(autouse=True, params=[False])
def __mock_sys_stdin(request):
	stdin = StringIO("YES" if request.param else "no")
	with patch.object(sys, 'stdin', stdin) as mock_object:
		yield mock_object

@pytest.fixture(autouse=True)
def __mock_sync_program_name():
	with patch.object(
		mode_add_model_executor,
		"_SYNC_PROGRAM_NAME",
		mode_add_model.SYNC_PROGRAM_NAME
	) as mock_object:
		yield mock_object
