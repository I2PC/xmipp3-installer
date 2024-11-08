from unittest.mock import patch, call, Mock

import pytest

from xmipp3_installer.installer.handlers import git_handler

from .... import get_assertion_message

__CWD = "/path/to/dummy"
__COMMIT1 = "4156gc81921is"
__COMMIT2 = "792cq86301pqw"

def test_calls_run_shell_command_when_getting_current_branch(
	__mock_run_shell_command
):
	git_handler.get_current_branch(dir=__CWD)
	__mock_run_shell_command.assert_called_once_with(
		"git rev-parse --abbrev-ref HEAD",
		cwd=__CWD
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
	git_handler.is_tag(dir=__CWD)
	__mock_get_current_branch.assert_called_once_with(dir=__CWD)

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

def test_calls_get_current_branch_when_checking_if_branch_is_up_to_date(
	__mock_get_current_branch,
	__mock_run_shell_command
):
	git_handler.is_branch_up_to_date(dir=__CWD)
	__mock_get_current_branch.assert_called_once_with(dir=__CWD)

def test_calls_run_shell_command_when_checking_if_branch_is_up_to_date(
	__mock_get_current_branch,
	__mock_run_shell_command
):
	git_handler.is_branch_up_to_date(dir=__CWD)
	__mock_run_shell_command.assert_has_calls([
		call("git fetch", cwd=__CWD),
		call(f"git rev-parse {__mock_get_current_branch()}", cwd=__CWD),
		call(f"git rev-parse origin/{__mock_get_current_branch()}")
	])

@pytest.mark.parametrize(
	"__mock_get_current_branch,run_shell_command_returns,expected_is_up_to_date",
	[
		pytest.param(None, [(0, ""), (0, __COMMIT1), (0, __COMMIT1)], False),
		pytest.param("main", [(1, ""), (0, __COMMIT1), (0, __COMMIT1)], False),
		pytest.param("main", [(0, ""), (0, __COMMIT1), (1, __COMMIT1)], False),
		pytest.param("main", [(0, ""), (0, __COMMIT1), (0, __COMMIT2)], False),
		pytest.param("main", [(0, ""), (1, __COMMIT1), (0, __COMMIT1)], True),
		pytest.param("main", [(0, ""), (1, __COMMIT2), (0, __COMMIT1)], False),
		pytest.param("main", [(0, ""), (0, __COMMIT1), (0, __COMMIT1)], True)
	],
	indirect=["__mock_get_current_branch"]
)
def test_returns_expected_value_when_checking_if_branch_is_up_to_date(
	__mock_get_current_branch,
	run_shell_command_returns,
	expected_is_up_to_date
):
	mock_run_shell_command = Mock()
	mock_run_shell_command.side_effect = [
		__return_unchanged(return_value)
		for return_value in run_shell_command_returns
	]
	with patch(
		"xmipp3_installer.installer.handlers.shell_handler.run_shell_command",
		new=mock_run_shell_command,
	):
		is_up_to_date = git_handler.is_branch_up_to_date(dir=__CWD)
		assert (
			is_up_to_date == expected_is_up_to_date
		), get_assertion_message("is branch up to date result", expected_is_up_to_date, is_up_to_date)

def __return_unchanged(value):
	return value

@pytest.fixture(params=[(0, "default_output")])
def __mock_run_shell_command(request):
	with patch(
		"xmipp3_installer.installer.handlers.shell_handler.run_shell_command"
	) as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(params=["default_branch"])
def __mock_get_current_branch(request):
	with patch(
		"xmipp3_installer.installer.handlers.git_handler.get_current_branch"
	) as mock_method:
		mock_method.return_value = request.param
		yield mock_method
