import sys
from io import StringIO
from unittest.mock import patch

import pytest

from xmipp3_installer.application.cli import cli
from xmipp3_installer.application.cli import arguments
from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.application.cli.arguments import modes
from xmipp3_installer.installer.modes.mode_models import mode_models_executor

from .shell_command_outputs import mode_get_models
from .. import get_assertion_message, normalize_text_line_endings

@pytest.mark.parametrize(
	"__mock_sync_program_path,__mock_os_path_isdir,expected_message",
	[
		pytest.param(False, False, mode_get_models.NO_PROGRAM),
		 pytest.param(False, True, mode_get_models.NO_PROGRAM),
		pytest.param(True, False, mode_get_models.DOWNLOAD),
		pytest.param(True, True, mode_get_models.UPDATE)
	],
	indirect=["__mock_sync_program_path", "__mock_os_path_isdir"]
)
def test_get_models(
	__mock_sys_argv,
	__mock_sync_program_path,
	__mock_os_path_isdir,
	expected_message,
	__mock_stdout_stderr
):
	stdout, _ = __mock_stdout_stderr
	with pytest.raises(SystemExit):
		cli.main()
	output = normalize_text_line_endings(stdout.getvalue())
	assert (
		output == expected_message
	), get_assertion_message("get models output", expected_message, output)

@pytest.fixture(autouse=True)
def __mock_sys_argv():
	args = [
		arguments.XMIPP_PROGRAM_NAME,
		modes.MODE_GET_MODELS,
		params.PARAMS[params.PARAM_MODELS_DIRECTORY][params.SHORT_VERSION],
		mode_get_models.REAL_MODELS_DIR
	]
	with patch.object(sys, 'argv', args) as mock_object:
		yield mock_object

@pytest.fixture
def __mock_stdout_stderr():
	new_stdout, new_stderr = StringIO(), StringIO()
	with patch('sys.stdout', new=new_stdout), patch('sys.stderr', new=new_stderr):
		yield new_stdout, new_stderr

@pytest.fixture(autouse=True)
def __mock_sync_program_name():
	with patch.object(
		mode_models_executor,
		"_SYNC_PROGRAM_NAME",
		mode_get_models.SYNC_PROGRAM_NAME
	) as mock_object:
		yield mock_object

@pytest.fixture(autouse=True, params=[False])
def __mock_sync_program_path(request):
	new_value = (
		mode_get_models.MODEL_DIR 
		if request.param else 
		mode_models_executor._SYNC_PROGRAM_PATH
	)
	with patch.object(
		mode_models_executor,
		"_SYNC_PROGRAM_PATH",
		new_value
	) as mock_object:
		yield mock_object

@pytest.fixture(autouse=True, params=[False])
def __mock_os_path_isdir(request):
	with patch("os.path.isdir") as mock_method:
		mock_method.return_value = request.param
		yield mock_method
