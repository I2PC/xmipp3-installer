import sys
from io import StringIO
from unittest.mock import patch

import pytest

from xmipp3_installer.application.cli import cli
from xmipp3_installer.application.cli.parsers import format
from xmipp3_installer.application.cli import arguments

from . import terminal_sizes, general_message
from .... import get_assertion_message, MockTerminalSize

@pytest.mark.parametrize(
	"__mock_get_terminal_column_size,__mock_sys_argv,message_object",
	[
		pytest.param(
			terminal_sizes.LARGE_TERMINAL_WIDTH,
			[],
			general_message.GENERAL_HELP_MESSAGE
		),
		pytest.param(
			terminal_sizes.SHORT_TERMINAL_WIDTH,
			[],
			general_message.GENERAL_HELP_MESSAGE
		)
	],
	indirect=["__mock_get_terminal_column_size", "__mock_sys_argv"]
)
def test_prints_expected_help_message(
	__mock_get_terminal_column_size,
	message_object,
	__mock_stdout_stderr,
	__mock_tab_size,
	__mock_sys_argv
):
	stdout, _ = __mock_stdout_stderr
	expected_message = message_object[__mock_get_terminal_column_size().columns]
	with pytest.raises(SystemExit):
		cli.main()
	stdout_value = stdout.getvalue()
	assert (
		stdout_value == expected_message
	), get_assertion_message("help message", expected_message, stdout_value)

@pytest.fixture
def __mock_get_terminal_column_size(request):
	with patch("shutil.get_terminal_size") as mock_method:
		width = request.param if hasattr(request, "param") else terminal_sizes.LARGE_TERMINAL_WIDTH
		mock_method.return_value = MockTerminalSize(width)
		yield mock_method

@pytest.fixture
def __mock_stdout_stderr():
	new_stdout, new_stderr = StringIO(), StringIO()
	with patch('sys.stdout', new=new_stdout), patch('sys.stderr', new=new_stderr):
		yield new_stdout, new_stderr
		from xmipp3_installer.application.logger.logger import logger

@pytest.fixture
def __mock_tab_size(request):
	tab_size = request.param if hasattr(request, "param") else 4
	with patch.object(format, "TAB_SIZE", tab_size):
		yield

@pytest.fixture
def __mock_sys_argv(request):
	args = request.param if hasattr(request, "param") else []
	with patch.object(sys, 'argv', [arguments.XMIPP_PROGRAM_NAME, *args, "-h"]):
		yield
