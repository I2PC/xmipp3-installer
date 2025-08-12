import sys
from io import StringIO
from unittest.mock import patch

import pytest

from xmipp3_installer.application.cli import arguments, cli
from xmipp3_installer.application.cli.arguments import modes, params
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.installer.modes.mode_sync import mode_sync_executor
from xmipp3_installer.shared import file_operations

from .shell_command_outputs import mode_sync
from .shell_command_outputs.mode_sync import mode_get_models
from .. import (
  get_assertion_message, normalize_text_line_endings,
  TEST_FILES_DIR, create_versions_json_file, remove_formatting_characters
)

@pytest.mark.parametrize(
  "__mock_sync_program_path,__mock_os_path_isdir,expected_message",
  [
    pytest.param(False, False, mode_sync.NO_PROGRAM, id="Non-existing program download"),
    pytest.param(False, True, mode_sync.NO_PROGRAM, id="Non-existing program update"),
    pytest.param(True, False, mode_get_models.DOWNLOAD, id="Existing program download"),
    pytest.param(True, True, mode_get_models.UPDATE, id="Existing program update")
  ],
  indirect=["__mock_sync_program_path", "__mock_os_path_isdir"]
)
def test_get_models(
  __mock_sys_argv,
  __mock_sync_program_path,
  __mock_os_path_isdir,
  expected_message,
  __mock_stdout_stderr,
  __setup_environment
):
  stdout, _ = __mock_stdout_stderr
  with pytest.raises(SystemExit):
    cli.main()
  output = remove_formatting_characters(
    normalize_text_line_endings(stdout.getvalue())
  )
  normalized_expected_message = remove_formatting_characters(expected_message)
  assert (
    output == normalized_expected_message
  ), get_assertion_message("get models output", normalized_expected_message, output)

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

@pytest.fixture(autouse=True, params=[False])
def __mock_os_path_isdir(request):
  with patch("os.path.isdir") as mock_method:
    mock_method.return_value = request.param
    yield mock_method

@pytest.fixture
def __setup_environment():
  try:
    create_versions_json_file()
    yield
  finally:
    file_operations.delete_paths([
      paths.VERSION_INFO_FILE
    ])
