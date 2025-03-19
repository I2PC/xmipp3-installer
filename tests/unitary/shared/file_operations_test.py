from unittest.mock import patch, call

import pytest

from xmipp3_installer.shared import file_operations

from ... import get_assertion_message

__PATHS = ['/path/to/file1', '/path/to/file2']
__NUMBER_OF_CALLS_TEXT = "number of calls"

@pytest.mark.parametrize(
  "paths",
  [
    pytest.param([__PATHS[0]]),
    pytest.param([__PATHS[1]]),
    pytest.param(__PATHS)
  ]
)
def test_calls_os_path_exists_for_each_path_when_deleting_paths(
  paths,
  __mock_os_path_exists
):
  __mock_os_path_exists.return_value = False
  file_operations.delete_paths(paths)
  expected_calls = [
    call(path) for path in paths
  ]
  __mock_os_path_exists.assert_has_calls(expected_calls)
  assert (
    len(paths) == __mock_os_path_exists.call_count
  ), get_assertion_message(__NUMBER_OF_CALLS_TEXT, len(paths), __mock_os_path_exists.call_count)

@pytest.mark.parametrize(
  "paths",
  [
    pytest.param([__PATHS[0]]),
    pytest.param([__PATHS[1]]),
    pytest.param(__PATHS)
  ]
)
def test_calls_isdir_when_deleting_paths_that_exist(
  paths,
  __mock_os_path_isdir
):
  file_operations.delete_paths(paths)
  expected_calls = [
    call(path) for path in paths
  ]
  __mock_os_path_isdir.assert_has_calls(expected_calls)
  assert (
    len(paths) == __mock_os_path_isdir.call_count
  ), get_assertion_message(__NUMBER_OF_CALLS_TEXT, len(paths), __mock_os_path_isdir.call_count)

@pytest.mark.parametrize(
  "paths",
  [
    pytest.param([__PATHS[0]]),
    pytest.param([__PATHS[1]]),
    pytest.param(__PATHS)
  ]
)
def test_calls_rmtree_when_deleting_dirs_that_exist(
  paths,
  __mock_os_path_isdir,
  __mock_rmtree
):
  __mock_os_path_isdir.return_value = True
  file_operations.delete_paths(paths)
  expected_calls = [
    call(path, ignore_errors=True) for path in paths
  ]
  __mock_rmtree.assert_has_calls(expected_calls)
  assert (
    len(paths) == __mock_rmtree.call_count
  ), get_assertion_message(__NUMBER_OF_CALLS_TEXT, len(paths), __mock_rmtree.call_count)

@pytest.mark.parametrize(
  "paths",
  [
    pytest.param([__PATHS[0]]),
    pytest.param([__PATHS[1]]),
    pytest.param(__PATHS)
  ]
)
def test_calls_os_remove_when_deleting_files_that_exist(
  paths,
  __mock_os_remove
):
  file_operations.delete_paths(paths)
  expected_calls = [
    call(path) for path in paths
  ]
  __mock_os_remove.assert_has_calls(expected_calls)
  assert (
    len(paths) == __mock_os_remove.call_count
  ), get_assertion_message(__NUMBER_OF_CALLS_TEXT, len(paths), __mock_os_remove.call_count)

def test_does_not_call_isdir_rmtree_os_remove_when_deleting_paths_that_do_not_exist(
  __mock_os_path_exists,
  __mock_os_path_isdir,
  __mock_rmtree,
  __mock_os_remove
):
  __mock_os_path_exists.return_value = False
  file_operations.delete_paths(__PATHS)
  __mock_os_path_isdir.assert_not_called()
  __mock_rmtree.assert_not_called()
  __mock_os_remove.assert_not_called()

def test_does_not_call_rmtree_when_deleting_files(
  __mock_rmtree
):
  file_operations.delete_paths(__PATHS)
  __mock_rmtree.assert_not_called()

def test_does_not_call_os_remove_when_deleting_dirs(
  __mock_os_path_isdir,
  __mock_os_remove
):
  __mock_os_path_isdir.return_value = True
  file_operations.delete_paths(__PATHS)
  __mock_os_remove.assert_not_called()

@pytest.fixture(params=[True], autouse=True)
def __mock_os_path_exists(request):
  with patch("os.path.exists") as mock_method:
    mock_method.return_value = request.param
    yield mock_method

@pytest.fixture(params=[False], autouse=True)
def __mock_os_path_isdir(request):
  with patch("os.path.isdir") as mock_method:
    mock_method.return_value = request.param
    yield mock_method

@pytest.fixture(autouse=True)
def __mock_rmtree():
  with patch("shutil.rmtree") as mock_method:
    yield mock_method

@pytest.fixture(autouse=True)
def __mock_os_remove():
  with patch("os.remove") as mock_method:
    yield mock_method
