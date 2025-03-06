from unittest.mock import patch, call, Mock

import pytest

from xmipp3_installer.installer.handlers import git_handler

from .... import get_assertion_message

__CWD = "/path/to/dummy"
__COMMIT1 = "4156gc81921is"
__COMMIT2 = "792cq86301pqw"
__SHORT_COMMIT = "5c3a24f"
__TAG_NAME = "tags/v3.24.06-Oceanus"
__RAW_COMMIT_NAME = f"{__SHORT_COMMIT} tags/v3.24.06-Oceanus"
__BRANCH_NAME = "devel"
__REF_TAG_NAME = "v1.0.0"
__GIT_LS_REMOTE_OUTPUT_BRANCH = f"4fb11a33809108b5f4550ac2657cb7cac448253f\trefs/heads/{__BRANCH_NAME}"
__GIT_LS_REMOTE_OUTPUT_TAG = f"4fb11a33809108b5f4550ac2657cb7cac448253f\trefs/tags/{__REF_TAG_NAME}"
__GIT_COMMAND = "git command"
__SOURCE = "source"
__SOURCE_PATH = "/path/to/source"

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

def test_calls_run_shell_command_when_getting_current_commit(__mock_run_shell_command):
	git_handler.get_current_commit()
	__mock_run_shell_command.assert_called_once_with(
		"git rev-parse --short HEAD",
		cwd="./"
	)

@pytest.mark.parametrize(
	"__mock_run_shell_command,expected_commit",
	[
		pytest.param((1, ""), ""),
		pytest.param((1, __SHORT_COMMIT), ""),
		pytest.param((0, ""), ""),
		pytest.param((0, __SHORT_COMMIT), __SHORT_COMMIT)
	],
	indirect=["__mock_run_shell_command"]
)
def test_returns_expected_current_commit(__mock_run_shell_command, expected_commit):
	current_commit = git_handler.get_current_commit()
	assert (
		current_commit == expected_commit
	), get_assertion_message("current commit hash", expected_commit, current_commit)

def test_calls_run_shell_command_when_getting_commit_branch(__mock_run_shell_command):
	git_handler.get_commit_branch(__COMMIT1)
	__mock_run_shell_command.assert_called_once_with(
		f"git name-rev {__COMMIT1}",
		cwd="./"
	)

@pytest.mark.parametrize(
	"__mock_run_shell_command,expected_commit_branch",
	[
		pytest.param((1, ""), ""),
		pytest.param((1, __RAW_COMMIT_NAME), ""),
		pytest.param((0, ""), ""),
		pytest.param((0, __RAW_COMMIT_NAME), __TAG_NAME)
	],
	indirect=["__mock_run_shell_command"]
)
def test_returns_expected_commit_branch(__mock_run_shell_command, expected_commit_branch):
	commit_branch = git_handler.get_commit_branch(__SHORT_COMMIT)
	assert (
		commit_branch == expected_commit_branch
	), get_assertion_message("commit branch", expected_commit_branch, commit_branch)

@pytest.mark.parametrize(
	"repo,branch",
	[
		pytest.param("repo1", "branch1"),
		pytest.param("repo2", "branch2")
	]
)
def test_calls_ref_exists_in_repo_when_checking_if_branch_exists(
	repo,
	branch,
	__mock_ref_exists_in_repo
):
	git_handler.branch_exists_in_repo(repo, branch)
	__mock_ref_exists_in_repo.assert_called_once_with(
		repo, branch, True
	)

@pytest.mark.parametrize(
	"__mock_ref_exists_in_repo",
	[pytest.param(False), pytest.param(True)],
	indirect=["__mock_ref_exists_in_repo"]
)
def test_returns_expected_value_when_checking_if_branch_exists(
	__mock_ref_exists_in_repo
):
	exists = git_handler.branch_exists_in_repo("repo_url", __BRANCH_NAME)
	assert (
		exists == __mock_ref_exists_in_repo()
	), get_assertion_message("branch existence value", __mock_ref_exists_in_repo(), exists)

@pytest.mark.parametrize(
	"repo,tag",
	[
		pytest.param("repo1", "tag1"),
		pytest.param("repo2", "tag2")
	]
)
def test_calls_ref_exists_in_repo_when_checking_if_tag_exists(
	repo,
	tag,
	__mock_ref_exists_in_repo
):
	git_handler.tag_exists_in_repo(repo, tag)
	__mock_ref_exists_in_repo.assert_called_once_with(
		repo, tag, False
	)

@pytest.mark.parametrize(
	"__mock_ref_exists_in_repo",
	[pytest.param(False), pytest.param(True)],
	indirect=["__mock_ref_exists_in_repo"]
)
def test_returns_expected_value_when_checking_if_tag_exists(
	__mock_ref_exists_in_repo
):
	exists = git_handler.tag_exists_in_repo("repo_url", __REF_TAG_NAME)
	assert (
		exists == __mock_ref_exists_in_repo()
	), get_assertion_message("tag existence value", __mock_ref_exists_in_repo(), exists)

@pytest.mark.parametrize(
	"is_branch,repo,ref,expected_ref_type",
	[
		pytest.param(False, "repo1", "ref1", "tags"),
		pytest.param(False, "repo2", "ref2", "tags"),
		pytest.param(True, "repo1", "ref1", "heads"),
		pytest.param(True, "repo2", "ref2", "heads")
	]
)
def test_calls_run_shell_command_when_checking_if_ref_exists(
	is_branch,
	repo,
	ref,
	expected_ref_type,
	__mock_run_shell_command
):
	git_handler.__ref_exists_in_repo(repo, ref, is_branch)
	__mock_run_shell_command.assert_called_once_with(
		f"git ls-remote --{expected_ref_type} {repo}.git refs/{expected_ref_type}/{ref}"
	)

@pytest.mark.parametrize(
	"__mock_run_shell_command,ref_name,is_branch,expected_exists",
	[
		pytest.param((1, "some output"), __BRANCH_NAME, False, False),
		pytest.param((1, "some output"), __BRANCH_NAME, True, False),
		pytest.param((1, "some output"), __REF_TAG_NAME, False, False),
		pytest.param((1, "some output"), __REF_TAG_NAME, True, False),
		pytest.param((1, __GIT_LS_REMOTE_OUTPUT_BRANCH), __BRANCH_NAME, False, False),
		pytest.param((1, __GIT_LS_REMOTE_OUTPUT_BRANCH), __BRANCH_NAME, True, False),
		pytest.param((1, __GIT_LS_REMOTE_OUTPUT_BRANCH), __REF_TAG_NAME, False, False),
		pytest.param((1, __GIT_LS_REMOTE_OUTPUT_BRANCH), __REF_TAG_NAME, True, False),
		pytest.param((1, __GIT_LS_REMOTE_OUTPUT_TAG), __BRANCH_NAME, False, False),
		pytest.param((1, __GIT_LS_REMOTE_OUTPUT_TAG), __BRANCH_NAME, True, False),
		pytest.param((1, __GIT_LS_REMOTE_OUTPUT_TAG), __REF_TAG_NAME, False, False),
		pytest.param((1, __GIT_LS_REMOTE_OUTPUT_TAG), __REF_TAG_NAME, True, False),
		pytest.param((0, __GIT_LS_REMOTE_OUTPUT_BRANCH), __BRANCH_NAME, False, False),
		pytest.param((0, __GIT_LS_REMOTE_OUTPUT_BRANCH), __BRANCH_NAME, True, True),
		pytest.param((0, __GIT_LS_REMOTE_OUTPUT_TAG), __BRANCH_NAME, False, False),
		pytest.param((0, __GIT_LS_REMOTE_OUTPUT_TAG), __BRANCH_NAME, True, False),
		pytest.param((0, __GIT_LS_REMOTE_OUTPUT_BRANCH), __REF_TAG_NAME, False, False),
		pytest.param((0, __GIT_LS_REMOTE_OUTPUT_BRANCH), __REF_TAG_NAME, True, False),
		pytest.param((0, __GIT_LS_REMOTE_OUTPUT_TAG), __REF_TAG_NAME, False, True),
		pytest.param((0, __GIT_LS_REMOTE_OUTPUT_TAG), __REF_TAG_NAME, True, False)
	],
	indirect=["__mock_run_shell_command"]
)
def test_returns_expected_value_when_checking_if_ref_exists(
	__mock_run_shell_command,
	ref_name,
	is_branch,
	expected_exists
):
	exists = git_handler.__ref_exists_in_repo("repo_url", ref_name, is_branch)
	assert (
		exists == expected_exists
	), get_assertion_message("ref existence value", expected_exists, exists)

@pytest.mark.parametrize(
	"repo,branch",
	[
		pytest.param("repo1", "branch1"),
		pytest.param("repo2", "branch2")
	]
)
def test_calls_branch_exists_in_repo_when_getting_clonable_branch(
	repo,
	branch,
	__mock_branch_exists_in_repo,
	__mock_tag_exists_in_repo
):
	git_handler.get_clonable_branch(repo, branch, "tag_name")
	__mock_branch_exists_in_repo.assert_called_once_with(repo, branch)

@pytest.mark.parametrize(
	"repo,branch,tag",
	[
		pytest.param("repo1", "branch1", "tag1"),
		pytest.param("repo2", "branch2", "tag2")
	]
)
def test_calls_tag_exists_in_repo_when_getting_clonable_branch_and_branch_does_not_exist(
	repo,
	branch,
	tag,
	__mock_branch_exists_in_repo,
	__mock_tag_exists_in_repo
):
	__mock_branch_exists_in_repo.return_value = False
	git_handler.get_clonable_branch(repo, branch, tag)
	__mock_tag_exists_in_repo.assert_called_once_with(repo, tag)

def test_does_not_call_tag_exists_in_repo_when_getting_clonable_branch_and_branch_exists(
	__mock_branch_exists_in_repo,
	__mock_tag_exists_in_repo
):
	git_handler.get_clonable_branch("repo", "branch", "tag")
	__mock_tag_exists_in_repo.assert_not_called()

@pytest.mark.parametrize(
	"target_branch,"
	"viable_tag,"
	"__mock_branch_exists_in_repo,"
	"__mock_tag_exists_in_repo,"
	"expected_clonable_branch",
	[
		pytest.param(None, None, False, False, None),
		pytest.param(None, None, False, True, None),
		pytest.param(None, None, True, False, None),
		pytest.param(None, None, True, True, None),
		pytest.param(None, __REF_TAG_NAME, False, False, None),
		pytest.param(None, __REF_TAG_NAME, False, True, __REF_TAG_NAME),
		pytest.param(None, __REF_TAG_NAME, True, False, None),
		pytest.param(None, __REF_TAG_NAME, True, True, __REF_TAG_NAME),
		pytest.param(__BRANCH_NAME, None, False, False, None),
		pytest.param(__BRANCH_NAME, None, False, True, None),
		pytest.param(__BRANCH_NAME, None, True, False, __BRANCH_NAME),
		pytest.param(__BRANCH_NAME, None, True, True, __BRANCH_NAME),
		pytest.param(__BRANCH_NAME, __REF_TAG_NAME, False, False, None),
		pytest.param(__BRANCH_NAME, __REF_TAG_NAME, False, True, __REF_TAG_NAME),
		pytest.param(__BRANCH_NAME, __REF_TAG_NAME, True, False, __BRANCH_NAME),
		pytest.param(__BRANCH_NAME, __REF_TAG_NAME, True, True, __BRANCH_NAME)
	],
	indirect=[
		"__mock_branch_exists_in_repo",
		"__mock_tag_exists_in_repo"
	]
)
def test_returns_expected_clonable_branch(
	target_branch,
	viable_tag,
	__mock_branch_exists_in_repo,
	__mock_tag_exists_in_repo,
	expected_clonable_branch
):
	clonable_branch = git_handler.get_clonable_branch(
		"repo", target_branch, viable_tag
	)
	assert (
		clonable_branch == expected_clonable_branch
	), get_assertion_message(
		"clonable branch",
		expected_clonable_branch,
		clonable_branch
	)

def test_calls_get_source_path_when_executing_git_command_for_source(
	__mock_get_path_source,
	__mock_run_shell_command
):
	git_handler.execute_git_command_for_source(__GIT_COMMAND, __SOURCE)
	__mock_get_path_source.assert_called_once_with(__SOURCE)

def test_calls_logger_if_source_path_does_not_exist_when_executing_git_command_for_source(
	__mock_os_path_exists,
	__mock_get_path_source,
	__mock_logger,
	__mock_logger_yellow
):
	__mock_os_path_exists.return_value = False
	git_handler.execute_git_command_for_source(__GIT_COMMAND, __SOURCE)
	__mock_logger.assert_called_once_with(__mock_logger_yellow(
		f"WARNING: Source {__SOURCE} does not exist in path {__mock_get_path_source(__SOURCE)}. Skipping."
	))

def test_does_not_call_logger_if_source_path_exists_when_executing_git_command_for_source(
	__mock_logger,
	__mock_run_shell_command
):
	git_handler.execute_git_command_for_source(__GIT_COMMAND, __SOURCE)
	__mock_logger.assert_not_called()

def test_calls_run_shell_command_if_source_path_exists_when_executing_git_command_for_source(
	__mock_get_path_source,
	__mock_run_shell_command
):
	git_handler.execute_git_command_for_source(__GIT_COMMAND, __SOURCE)
	__mock_run_shell_command.assert_called_once_with(
		f"git {__GIT_COMMAND}",
		cwd=__mock_get_path_source(__SOURCE),
		show_output=True,
		show_error=True
	)

def test_does_not_call_run_shell_command_if_source_path_does_not_exist_when_executing_git_command_for_source(
	__mock_os_path_exists,
	__mock_run_shell_command
):
	__mock_os_path_exists.return_value = False
	git_handler.execute_git_command_for_source(__GIT_COMMAND, __SOURCE)
	__mock_run_shell_command.assert_not_called()

@pytest.mark.parametrize(
	"__mock_os_path_exists,__mock_run_shell_command,expected_result",
	[
		pytest.param(False, (1, "error"), (0, "")),
		pytest.param(False, (0, "success"), (0, "")),
		pytest.param(True, (1, "error"), (1, "error")),
		pytest.param(True, (0, "success"), (0, "success"))
	],
	indirect=["__mock_os_path_exists", "__mock_run_shell_command"]
)
def test_returns_expected_result_when_executing_git_command_for_source(
	__mock_os_path_exists,
	__mock_run_shell_command,
	expected_result
):
	result = git_handler.execute_git_command_for_source(__GIT_COMMAND, __SOURCE)
	assert (
		result == expected_result
	), get_assertion_message("git command on source result", expected_result, result)

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

@pytest.fixture(params=[True])
def __mock_ref_exists_in_repo(request):
	with patch(
		"xmipp3_installer.installer.handlers.git_handler.__ref_exists_in_repo"
	) as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(params=[True])
def __mock_branch_exists_in_repo(request):
	with patch(
		"xmipp3_installer.installer.handlers.git_handler.branch_exists_in_repo"
	) as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(params=[True])
def __mock_tag_exists_in_repo(request):
	with patch(
		"xmipp3_installer.installer.handlers.git_handler.tag_exists_in_repo"
	) as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_get_path_source():
	with patch(
		"xmipp3_installer.installer.constants.paths.get_source_path"
	) as mock_method:
		mock_method.return_value = __SOURCE_PATH
		yield mock_method

@pytest.fixture(params=[True], autouse=True)
def __mock_os_path_exists(request):
	with patch("os.path.exists") as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_logger():
	with patch(
		"xmipp3_installer.application.logger.logger.Logger.__call__"
	) as mock_method:
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_logger_yellow():
	with patch(
		"xmipp3_installer.application.logger.logger.Logger.yellow"
	) as mock_method:
		mock_method.side_effect = lambda text: f"yellow-{text}-yellow"
		yield mock_method
