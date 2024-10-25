from unittest.mock import patch

import pytest

from xmipp3_installer.domain.handlers import git_handler

from .... import get_assertion_message

def test_calls_run_shell_command_when_getting_current_branch(
  __mock_run_shell_command
):
  cwd = "/path/to/dummy"
  git_handler.get_current_branch(dir=cwd)
  __mock_run_shell_command.assert_called_once_with(
    "git rev-parse --abbrev-ref HEAD",
    cwd=cwd
  )

@pytest.mark.parametrize(
  "__mock_run_shell_command,expected_branch_name",
  [
    pytest.param((0, "test_branch_name"), "test_branch_name"),
    pytest.param((1, "test_branch_name"), "")
  ],
  indirect=["__mock_run_shell_command"]
)
def test_returns_expected_branch_when_getting_current_branch(
  __mock_run_shell_command,
  expected_branch_name
):
  branch_name = git_handler.get_current_branch()
  assert (
    branch_name == expected_branch_name
  ), get_assertion_message("branch name", expected_branch_name, branch_name)

def test_calls_get_current_branch_when_checking_if_is_tag(
  __mock_get_current_branch
):
  cwd = "/path/to/dummy"
  git_handler.is_tag(dir=cwd)
  __mock_get_current_branch.assert_called_once_with(dir=cwd)

@pytest.mark.parametrize(
  "__mock_get_current_branch,expected_is_tag",
  [
    pytest.param("test_branch_name", False),
    pytest.param("HEAD", True),
    pytest.param(None, True)
  ],
  indirect=["__mock_get_current_branch"]
)
def test_returns_expected_result_when_checking_if_is_tag(
  __mock_get_current_branch,
  expected_is_tag
):
  is_tag = git_handler.is_tag()
  assert (
    is_tag == expected_is_tag
  ), get_assertion_message("is tag result", expected_is_tag, is_tag)

@pytest.fixture
def __mock_run_shell_command(request):
  return_values = request.param if hasattr(request, "param") else (0, "default_output")
  with patch(
    "xmipp3_installer.domain.handlers.shell_handler.run_shell_command"
  ) as mock_method:
    mock_method.return_value = return_values
    yield mock_method

@pytest.fixture
def __mock_get_current_branch(request):
  branch = request.param if hasattr(request, "param") else "default_branch"
  with patch(
    "xmipp3_installer.domain.handlers.git_handler.get_current_branch"
  ) as mock_method:
    mock_method.return_value = branch
    yield mock_method
