import sys
from io import StringIO
from unittest.mock import patch

import pytest

from xmipp3_installer.application.cli import cli
from xmipp3_installer.application.cli.parsers import format
from xmipp3_installer.application.cli import arguments

from . import general_message
from .terminal_sizes import LARGE_TERMINAL_WIDTH, SHORT_TERMINAL_WIDTH
from .mode_messages import (
  mode_all, mode_version, mode_compile_and_install, mode_config_build,
  mode_config, mode_get_models, mode_get_sources, mode_clean_bin,
  mode_clean_all, mode_test, mode_git, mode_add_model
)
from .... import get_assertion_message, MockTerminalSize

@pytest.mark.parametrize(
  "__mock_get_terminal_column_size,__mock_sys_argv,message_object",
  [
    pytest.param(LARGE_TERMINAL_WIDTH, [], general_message.HELP_MESSAGE),
    pytest.param(SHORT_TERMINAL_WIDTH, [], general_message.HELP_MESSAGE),
    pytest.param(LARGE_TERMINAL_WIDTH, ["version"], mode_version.HELP_MESSAGE),
    pytest.param(SHORT_TERMINAL_WIDTH, ["version"], mode_version.HELP_MESSAGE),
    pytest.param(LARGE_TERMINAL_WIDTH, ["compileAndInstall"], mode_compile_and_install.HELP_MESSAGE),
    pytest.param(SHORT_TERMINAL_WIDTH, ["compileAndInstall"], mode_compile_and_install.HELP_MESSAGE),
    pytest.param(LARGE_TERMINAL_WIDTH, ["all"], mode_all.HELP_MESSAGE),
    pytest.param(SHORT_TERMINAL_WIDTH, ["all"], mode_all.HELP_MESSAGE),
    pytest.param(LARGE_TERMINAL_WIDTH, ["configBuild"], mode_config_build.HELP_MESSAGE),
    pytest.param(SHORT_TERMINAL_WIDTH, ["configBuild"], mode_config_build.HELP_MESSAGE),
    pytest.param(LARGE_TERMINAL_WIDTH, ["config"], mode_config.HELP_MESSAGE),
    pytest.param(SHORT_TERMINAL_WIDTH, ["config"], mode_config.HELP_MESSAGE),
    pytest.param(LARGE_TERMINAL_WIDTH, ["getModels"], mode_get_models.HELP_MESSAGE),
    pytest.param(SHORT_TERMINAL_WIDTH, ["getModels"], mode_get_models.HELP_MESSAGE),
    pytest.param(LARGE_TERMINAL_WIDTH, ["getSources"], mode_get_sources.HELP_MESSAGE),
    pytest.param(SHORT_TERMINAL_WIDTH, ["getSources"], mode_get_sources.HELP_MESSAGE),
    pytest.param(LARGE_TERMINAL_WIDTH, ["cleanBin"], mode_clean_bin.HELP_MESSAGE),
    pytest.param(SHORT_TERMINAL_WIDTH, ["cleanBin"], mode_clean_bin.HELP_MESSAGE),
    pytest.param(LARGE_TERMINAL_WIDTH, ["cleanAll"], mode_clean_all.HELP_MESSAGE),
    pytest.param(SHORT_TERMINAL_WIDTH, ["cleanAll"], mode_clean_all.HELP_MESSAGE),
    pytest.param(LARGE_TERMINAL_WIDTH, ["test"], mode_test.HELP_MESSAGE),
    pytest.param(SHORT_TERMINAL_WIDTH, ["test"], mode_test.HELP_MESSAGE),
    pytest.param(LARGE_TERMINAL_WIDTH, ["git"], mode_git.HELP_MESSAGE),
    pytest.param(SHORT_TERMINAL_WIDTH, ["git"], mode_git.HELP_MESSAGE),
    pytest.param(LARGE_TERMINAL_WIDTH, ["addModel"], mode_add_model.HELP_MESSAGE),
    pytest.param(SHORT_TERMINAL_WIDTH, ["addModel"], mode_add_model.HELP_MESSAGE),
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
    width = request.param if hasattr(request, "param") else LARGE_TERMINAL_WIDTH
    mock_method.return_value = MockTerminalSize(width)
    yield mock_method

@pytest.fixture
def __mock_stdout_stderr():
  new_stdout, new_stderr = StringIO(), StringIO()
  with patch('sys.stdout', new=new_stdout), patch('sys.stderr', new=new_stderr):
    yield new_stdout, new_stderr

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
