import os
import sys
from io import StringIO
from unittest.mock import patch

import pytest

from xmipp3_installer.application.cli import cli
from xmipp3_installer.application.cli import arguments
from xmipp3_installer.application.cli.arguments import modes
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.installer.modes.mode_sync import mode_sync_executor
from xmipp3_installer.installer.modes.mode_sync import mode_test_executor
from xmipp3_installer.shared import file_operations

from .shell_command_outputs import mode_sync
from .shell_command_outputs.mode_sync import mode_test
from .. import (
  get_assertion_message, normalize_text_line_endings,
  TEST_FILES_DIR, create_versions_json_file
)

__INDIVIDUAL_TEST = "test1"
__MULTIPLE_TESTS = f"{__INDIVIDUAL_TEST} test2 test3"
__SHOW_PARAM = "--show"
__ALL_FUNCTIONS_PARAM = "--all-functions"
__ALL_PROGRAMS_PARAM = "--all-programs"

@pytest.mark.parametrize(
  "__mock_bashrc_path,__mock_sync_program_path,"
  "__mock_dataset_path,__mock_sys_argv,expected_message",
  [
    pytest.param(
      False, False, False, __INDIVIDUAL_TEST, mode_test.NON_BASHRC_FILE,
      id="Non-existing bashrc file, non-existing program, no dataset, individual test"
    ),
    pytest.param(
      False, False, False, __MULTIPLE_TESTS, mode_test.NON_BASHRC_FILE,
      id="Non-existing bashrc file, non-existing program, no dataset, multiple tests"
    ),
    pytest.param(
      False, False, False, __SHOW_PARAM, mode_test.NON_BASHRC_FILE,
      id="Non-existing bashrc file, non-existing program, no dataset, show"
    ),
    pytest.param(
      False, False, False, __ALL_FUNCTIONS_PARAM, mode_test.NON_BASHRC_FILE,
      id="Non-existing bashrc file, non-existing program, no dataset, all functions"
    ),
    pytest.param(
      False, False, False, __ALL_PROGRAMS_PARAM, mode_test.NON_BASHRC_FILE,
      id="Non-existing bashrc file, non-existing program, no dataset, all programs"
    ),
    pytest.param(
      False, False, True, __INDIVIDUAL_TEST, mode_test.NON_BASHRC_FILE,
      id="Non-existing bashrc file, non-existing program, existing dataset, individual test"
    ),
    pytest.param(
      False, False, True, __MULTIPLE_TESTS, mode_test.NON_BASHRC_FILE,
      id="Non-existing bashrc file, non-existing program, existing dataset, multiple tests"
    ),
    pytest.param(
      False, False, True, __SHOW_PARAM, mode_test.NON_BASHRC_FILE,
      id="Non-existing bashrc file, non-existing program, existing dataset, show"
    ),
    pytest.param(
      False, False, True, __ALL_FUNCTIONS_PARAM, mode_test.NON_BASHRC_FILE,
      id="Non-existing bashrc file, non-existing program, existing dataset, all functions"
    ),
    pytest.param(
      False, False, True, __ALL_PROGRAMS_PARAM, mode_test.NON_BASHRC_FILE,
      id="Non-existing bashrc file, non-existing program, existing dataset, all programs"
    ),
    pytest.param(
      False, True, False, __INDIVIDUAL_TEST, mode_test.NON_BASHRC_FILE,
      id="Non-existing bashrc file, existing program, no dataset, individual test"
    ),
    pytest.param(
      False, True, False, __MULTIPLE_TESTS, mode_test.NON_BASHRC_FILE,
      id="Non-existing bashrc file, existing program, no dataset, multiple tests"
    ),
    pytest.param(
      False, True, False, __SHOW_PARAM, mode_test.NON_BASHRC_FILE,
      id="Non-existing bashrc file, existing program, no dataset, show"
    ),
    pytest.param(
      False, True, False, __ALL_FUNCTIONS_PARAM, mode_test.NON_BASHRC_FILE,
      id="Non-existing bashrc file, existing program, no dataset, all functions"
    ),
    pytest.param(
      False, True, False, __ALL_PROGRAMS_PARAM, mode_test.NON_BASHRC_FILE,
      id="Non-existing bashrc file, existing program, no dataset, all programs"
    ),
    pytest.param(
      False, True, True, __INDIVIDUAL_TEST, mode_test.NON_BASHRC_FILE,
      id="Non-existing bashrc file, existing program, existing dataset, individual test"
    ),
    pytest.param(
      False, True, True, __MULTIPLE_TESTS, mode_test.NON_BASHRC_FILE,
      id="Non-existing bashrc file, existing program, existing dataset, multiple tests"
    ),
    pytest.param(
      False, True, True, __SHOW_PARAM, mode_test.NON_BASHRC_FILE,
      id="Non-existing bashrc file, existing program, existing dataset, show"
    ),
    pytest.param(
      False, True, True, __ALL_FUNCTIONS_PARAM, mode_test.NON_BASHRC_FILE,
      id="Non-existing bashrc file, existing program, existing dataset, all functions"
    ),
    pytest.param(
      False, True, True, __ALL_PROGRAMS_PARAM, mode_test.NON_BASHRC_FILE,
      id="Non-existing bashrc file, existing program, existing dataset, all programs"
    ),
    pytest.param(
      True, False, False, __INDIVIDUAL_TEST, mode_sync.NO_PROGRAM,
      id="Existing bashrc file, non-existing program, no dataset, individual test"
    ),
    pytest.param(
      True, False, False, __MULTIPLE_TESTS, mode_sync.NO_PROGRAM,
      id="Existing bashrc file, non-existing program, no dataset, multiple tests"
    ),
    pytest.param(
      True, False, False, __SHOW_PARAM, mode_sync.NO_PROGRAM,
      id="Existing bashrc file, non-existing program, no dataset, show"
    ),
    pytest.param(
      True, False, False, __ALL_FUNCTIONS_PARAM, mode_sync.NO_PROGRAM,
      id="Existing bashrc file, non-existing program, no dataset, all functions"
    ),
    pytest.param(
      True, False, False, __ALL_PROGRAMS_PARAM, mode_sync.NO_PROGRAM,
      id="Existing bashrc file, non-existing program, no dataset, all programs"
    ),
    pytest.param(
      True, False, True, __INDIVIDUAL_TEST, mode_sync.NO_PROGRAM,
      id="Existing bashrc file, non-existing program, existing dataset, individual test"
    ),
    pytest.param(
      True, False, True, __MULTIPLE_TESTS, mode_sync.NO_PROGRAM,
      id="Existing bashrc file, non-existing program, existing dataset, multiple tests"
    ),
    pytest.param(
      True, False, True, __SHOW_PARAM, mode_sync.NO_PROGRAM,
      id="Existing bashrc file, non-existing program, existing dataset, show"
    ),
    pytest.param(
      True, False, True, __ALL_FUNCTIONS_PARAM, mode_sync.NO_PROGRAM,
      id="Existing bashrc file, non-existing program, existing dataset, all functions"
    ),
    pytest.param(
      True, False, True, __ALL_PROGRAMS_PARAM, mode_sync.NO_PROGRAM,
      id="Existing bashrc file, non-existing program, existing dataset, all programs"
    ),
    pytest.param(
      True, True, False, __INDIVIDUAL_TEST, mode_test.get_download_message(__INDIVIDUAL_TEST),
      id="Existing bashrc file, existing program, no dataset, individual test"
    ),
    pytest.param(
      True, True, False, __MULTIPLE_TESTS, mode_test.get_download_message(__MULTIPLE_TESTS),
      id="Existing bashrc file, existing program, no dataset, multiple tests"
    ),
    pytest.param(
      True, True, False, __SHOW_PARAM, mode_test.get_download_message(""),
      id="Existing bashrc file, existing program, no dataset, show"
    ),
    pytest.param(
      True, True, False, __ALL_FUNCTIONS_PARAM, mode_test.get_download_message(""),
      id="Existing bashrc file, existing program, no dataset, all functions"
    ),
    pytest.param(
      True, True, False, __ALL_PROGRAMS_PARAM, mode_test.get_download_message(""),
      id="Existing bashrc file, existing program, no dataset, all programs"
    ),
    pytest.param(
      True, True, True, __INDIVIDUAL_TEST, mode_test.get_update_message(__INDIVIDUAL_TEST),
      id="Existing bashrc file, existing program, existing dataset, individual test"
    ),
    pytest.param(
      True, True, True, __MULTIPLE_TESTS, mode_test.get_update_message(__MULTIPLE_TESTS),
      id="Existing bashrc file, existing program, existing dataset, multiple tests"
    ),
    pytest.param(
      True, True, True, __SHOW_PARAM, mode_test.get_update_message(""),
      id="Existing bashrc file, existing program, existing dataset, show"
    ),
    pytest.param(
      True, True, True, __ALL_FUNCTIONS_PARAM, mode_test.get_update_message(""),
      id="Existing bashrc file, existing program, existing dataset, all functions"
    ),
    pytest.param(
      True, True, True, __ALL_PROGRAMS_PARAM, mode_test.get_update_message(""),
      id="Existing bashrc file, existing program, existing dataset, all programs"
    )
  ],
  indirect=[
    "__mock_bashrc_path",
    "__mock_sync_program_path",
    "__mock_dataset_path",
    "__mock_sys_argv"
  ]
)
def test_test(
  __mock_bashrc_path,
  __mock_sync_program_path,
  __mock_sys_argv,
  expected_message,
  __mock_stdout_stderr,
  __setup_environment
):
  stdout, _ = __mock_stdout_stderr
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
def __mock_python_test_script_name():
  new_name = os.path.basename(mode_test_executor._PYTHON_TEST_SCRIPT_NAME)
  with patch.object(
    mode_test_executor,
    "_PYTHON_TEST_SCRIPT_NAME",
    new_name
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

@pytest.fixture(autouse=True, params=[False])
def __mock_bashrc_path(request):
  new_path = os.path.join(
    TEST_FILES_DIR,
    mode_test.BASHRC_FILE_NAME
  ) if request.param else mode_test.NON_EXISTING_BASHRC_FILE_PATH
  with patch.object(
    mode_test_executor,
    "_BASHRC_FILE_PATH",
    new_path
  ) as mock_object:
    yield mock_object

@pytest.fixture
def __setup_environment():
  try:
    create_versions_json_file()
    yield
  finally:
    file_operations.delete_paths([
      paths.VERSION_INFO_FILE
    ])
