import sys
from io import StringIO
from unittest.mock import patch

import pytest

from xmipp3_installer.application.cli import cli
from xmipp3_installer.application.cli import arguments
from xmipp3_installer.application.cli.arguments import modes, params
from xmipp3_installer.installer.modes.mode_sync import mode_sync_executor
from xmipp3_installer.installer.modes.mode_sync import mode_test_executor

from .shell_command_outputs import mode_sync
from .shell_command_outputs.mode_sync import mode_test
from .. import get_assertion_message, normalize_text_line_endings, TEST_FILES_DIR

__INDIVIDUAL_TEST = "test1"
__MULTIPLE_TESTS = f"{__INDIVIDUAL_TEST} test2 test3"

@pytest.mark.parametrize(
	"__mock_sync_program_path,__mock_dataset_path,__mock_sys_argv,show,expected_message",
	[
		pytest.param(False, False, __INDIVIDUAL_TEST, False, mode_sync.NO_PROGRAM),
		pytest.param(False, False, __INDIVIDUAL_TEST, True, mode_sync.NO_PROGRAM),
		pytest.param(False, False, __MULTIPLE_TESTS, False, mode_sync.NO_PROGRAM),
		pytest.param(False, False, __MULTIPLE_TESTS, True, mode_sync.NO_PROGRAM),
		pytest.param(False, True, __INDIVIDUAL_TEST, False, mode_sync.NO_PROGRAM),
		pytest.param(False, True, __INDIVIDUAL_TEST, True, mode_sync.NO_PROGRAM),
		pytest.param(False, True, __MULTIPLE_TESTS, False, mode_sync.NO_PROGRAM),
		pytest.param(False, True, __MULTIPLE_TESTS, True, mode_sync.NO_PROGRAM),
		pytest.param(True, False, __INDIVIDUAL_TEST, False, mode_test.get_download_message(__INDIVIDUAL_TEST)),
		pytest.param(True, False, __INDIVIDUAL_TEST, True, mode_test.get_download_message(__INDIVIDUAL_TEST)),
		pytest.param(True, False, __MULTIPLE_TESTS, False, mode_test.get_download_message(__MULTIPLE_TESTS)),
		pytest.param(True, False, __MULTIPLE_TESTS, True, mode_test.get_download_message(__MULTIPLE_TESTS)),
		pytest.param(True, True, __INDIVIDUAL_TEST, False, mode_test.get_update_message(__INDIVIDUAL_TEST)),
		pytest.param(True, True, __INDIVIDUAL_TEST, True, mode_test.get_update_message(__INDIVIDUAL_TEST)),
		pytest.param(True, True, __MULTIPLE_TESTS, False, mode_test.get_update_message(__MULTIPLE_TESTS)),
		pytest.param(True, True, __MULTIPLE_TESTS, True, mode_test.get_update_message(__MULTIPLE_TESTS))
	],
	indirect=["__mock_sync_program_path", "__mock_dataset_path", "__mock_sys_argv"]
)
def test_add_model(
	__mock_sync_program_path,
	__mock_sys_argv,
	show,
	expected_message,
	__mock_stdout_stderr
):
	stdout, _ = __mock_stdout_stderr
	if show:
		__mock_sys_argv.append(params.PARAMS[params.PARAM_SHOW_TESTS][params.LONG_VERSION])
	with pytest.raises(SystemExit):
		cli.main()
	output = normalize_text_line_endings(stdout.getvalue())
	assert (
		output == expected_message
	), get_assertion_message("mode test output", expected_message, output)

@pytest.fixture(autouse=True, params=[__MULTIPLE_TESTS])
def __mock_sys_argv(request):
	params = [
		arguments.XMIPP_PROGRAM_NAME,
		modes.MODE_TEST,
		request.param
	]
	with patch.object(sys, 'argv', params) as mock_object:
		yield mock_object

@pytest.fixture
def __mock_stdout_stderr():
	new_stdout, new_stderr = StringIO(), StringIO()
	with patch('sys.stdout', new=new_stdout), patch('sys.stderr', new=new_stderr):
		yield new_stdout, new_stderr

@pytest.fixture(autouse=True)
def __mock_sync_program_name():
	with patch.object(
		mode_sync_executor,
		"_SYNC_PROGRAM_NAME",
		mode_sync.SYNC_PROGRAM_NAME
	) as mock_object:
		yield mock_object

@pytest.fixture(autouse=True, params=[False])
def __mock_sync_program_path(request):
	new_value = (
		TEST_FILES_DIR
		if request.param else
		mode_sync_executor._SYNC_PROGRAM_PATH
	)
	with patch.object(
		mode_sync_executor,
		"_SYNC_PROGRAM_PATH",
		new_value
	) as mock_object:
		yield mock_object

@pytest.fixture(autouse=True)
def __mock_python_test_script_path():
	with patch.object(
		mode_test_executor,
		"_PYTHON_TEST_SCRIPT_PATH",
		TEST_FILES_DIR
	) as mock_object:
		yield mock_object

@pytest.fixture(autouse=True)
def __mock_default_python_home():
	with patch.object(
		mode_test_executor,
		"_DEFAULT_PYTHON_HOME",
		"python"
	) as mock_object:
		yield mock_object

@pytest.fixture(autouse=True, params=[False])
def __mock_dataset_path(request, __mock_python_test_script_path):
	new_value = TEST_FILES_DIR if request.param else mode_test_executor._DATASET_PATH
	with patch.object(
		mode_test_executor,
		"_DATASET_PATH",
		new_value
	) as mock_object:
		yield mock_object
