from unittest.mock import patch, MagicMock, call

import pytest

from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.application.logger import errors
from xmipp3_installer.installer import constants, urls
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.installer.modes.mode_cmake.mode_cmake_executor import ModeCMakeExecutor
from xmipp3_installer.installer.modes.mode_cmake.mode_compile_and_install_executor import ModeCompileAndInstallExecutor

from .... import DummyVersionsManager
from ..... import get_assertion_message

__CMAKE = "cmake_executable"
__PARAM_BRANCH = "branch_param"
__PARAM_KEEP_OUTPUT = "keep-output"
__PARAM_JOBS = "param_jobs"
__PARAM_GIT_COMMAND = "git_command"
__BUILD_PATH = "build_path"
__BUILD_TYPE = "build_type"
__N_JOBS = 5
__CONTEXT = {
	__PARAM_BRANCH: None,
	constants.VERSIONS_CONTEXT_KEY: DummyVersionsManager(),
	__PARAM_KEEP_OUTPUT: False,
	__PARAM_JOBS: __N_JOBS
}
__CALL_COUNT_ASSERTION_MESSAGE = "call count"

def test_implements_interface_mode_cmake_executor():
	executor = ModeCompileAndInstallExecutor(__CONTEXT.copy())
	assert (
		isinstance(executor, ModeCMakeExecutor)
	), get_assertion_message(
		"parent class",
		ModeCMakeExecutor.__name__,
		executor.__class__.__bases__[0].__name__
	)

def test_overrides_expected_parent_config_values(__dummy_test_mode_cmake_executor):
	base_executor = __dummy_test_mode_cmake_executor(__CONTEXT.copy())
	compile_and_install_executor = ModeCompileAndInstallExecutor(__CONTEXT.copy())
	base_config = (
		base_executor.logs_to_file,
		base_executor.prints_with_substitution,
		not base_executor.prints_banner_on_exit,
		base_executor.sends_installation_info
	)
	inherited_config = (
		compile_and_install_executor.logs_to_file,
		compile_and_install_executor.prints_with_substitution,
		compile_and_install_executor.prints_banner_on_exit,
		compile_and_install_executor.sends_installation_info
	)
	assert (
		inherited_config == base_config
	), get_assertion_message("config values", base_config, inherited_config)

@pytest.mark.parametrize(
	"missing_param",
	[pytest.param(__PARAM_BRANCH), pytest.param(__PARAM_JOBS)]
)
def test_raises_key_error_if_params_not_in_context_when_initializing(missing_param):
	new_context = __CONTEXT.copy()
	del new_context[missing_param]
	with pytest.raises(KeyError):
		ModeCompileAndInstallExecutor(new_context)

@pytest.mark.parametrize(
	"branch,jobs",
	[
		pytest.param(None, None),
		pytest.param(constants.DEVEL_BRANCHNAME, __N_JOBS)
	]
)
def test_stores_expected_context_values_when_initializing(branch, jobs):
	executor = ModeCompileAndInstallExecutor({
		**__CONTEXT, __PARAM_BRANCH: branch, __PARAM_JOBS: jobs
	})
	stored_values = (executor.target_branch, executor.jobs)
	expected_values = (branch, jobs)
	assert (
		stored_values == expected_values
	), get_assertion_message("stored values", expected_values, stored_values)

def test_calls_branch_exists_in_repo_if_target_branch_provided_when_switching_branches(
	__mock_branch_exists_in_repo
):
	ModeCompileAndInstallExecutor(
		{**__CONTEXT, __PARAM_BRANCH: constants.DEVEL_BRANCHNAME}
	)._ModeCompileAndInstallExecutor__switch_branches()
	expected_calls = [
		call(f"{urls.I2PC_REPOSITORY_URL}{source}.git", constants.DEVEL_BRANCHNAME)
		for source in constants.XMIPP_SOURCES
	]
	__mock_branch_exists_in_repo.assert_has_calls(expected_calls)
	assert (
		__mock_branch_exists_in_repo.call_count == len(expected_calls)
	), get_assertion_message(
		__CALL_COUNT_ASSERTION_MESSAGE,
		len(expected_calls),
		__mock_branch_exists_in_repo.call_count
	)

def test_does_not_call_branch_exists_in_repo_if_target_branch_not_provided_when_switching_branches(
	__mock_branch_exists_in_repo
):
	ModeCompileAndInstallExecutor(
		__CONTEXT.copy()
	)._ModeCompileAndInstallExecutor__switch_branches()
	__mock_branch_exists_in_repo.assert_not_called()

@pytest.mark.parametrize(
	"branch_exists_in_repo",
	[
		pytest.param((False, False, False)),
		pytest.param((False, False, True)),
		pytest.param((False, True, False)),
		pytest.param((False, True, True)),
		pytest.param((True, False, False)),
		pytest.param((True, False, True)),
		pytest.param((True, True, False)),
		pytest.param((True, True, True))
	]
)
def test_calls_logger_if_branch_does_not_exist_in_repo_when_switching_branches(
	branch_exists_in_repo,
	__mock_branch_exists_in_repo,
	__mock_logger_yellow,
	__mock_logger
):
	__mock_branch_exists_in_repo.side_effect = branch_exists_in_repo
	ModeCompileAndInstallExecutor(
		{**__CONTEXT, __PARAM_BRANCH: constants.DEVEL_BRANCHNAME}
	)._ModeCompileAndInstallExecutor__switch_branches()
	expected_calls = [
		call(__mock_logger_yellow(
			f"WARNING: Branch {constants.DEVEL_BRANCHNAME} does not exist in source {source}. Skipping."
		))
		for exists, source in zip(branch_exists_in_repo, constants.XMIPP_SOURCES) if not exists
	]
	__mock_logger.assert_has_calls(expected_calls)
	assert (
		__mock_logger.call_count == len(expected_calls)
	), get_assertion_message(
		__CALL_COUNT_ASSERTION_MESSAGE,
		len(expected_calls),
		__mock_logger.call_count
	)

def test_calls_execute_git_command_for_source_if_target_branch_provided_and_exists_when_switching_branches(
	__mock_execute_git_command_for_source
):
	ModeCompileAndInstallExecutor(
		{**__CONTEXT, __PARAM_BRANCH: constants.DEVEL_BRANCHNAME}
	)._ModeCompileAndInstallExecutor__switch_branches()
	expected_calls = [
		call(f"checkout {constants.DEVEL_BRANCHNAME}", source)
		for source in constants.XMIPP_SOURCES
	]
	__mock_execute_git_command_for_source.assert_has_calls(expected_calls)
	assert (
		__mock_execute_git_command_for_source.call_count == len(expected_calls)
	), get_assertion_message(
		__CALL_COUNT_ASSERTION_MESSAGE,
		len(expected_calls),
		__mock_execute_git_command_for_source.call_count
	)

@pytest.mark.parametrize(
	"branch,__mock_branch_exists_in_repo",
	[
		pytest.param(None, False),
		pytest.param(None, True),
		pytest.param(constants.DEVEL_BRANCHNAME, False)
	],
	indirect=["__mock_branch_exists_in_repo"]
)
def test_does_not_call_execute_git_command_for_source_if_target_branch_not_provided_or_not_exists_when_switching_branches(
	branch,
	__mock_branch_exists_in_repo,
	__mock_execute_git_command_for_source
):
	ModeCompileAndInstallExecutor(
		{**__CONTEXT, __PARAM_BRANCH: branch}
	)._ModeCompileAndInstallExecutor__switch_branches()
	__mock_execute_git_command_for_source.assert_not_called()

@pytest.mark.parametrize(
	"branch,__mock_branch_exists_in_repo,"
	"__mock_execute_git_command_for_source,expected_result",
	[
		pytest.param(None, False, (1, "error"), (0, "")),
		pytest.param(None, False, (0, "success"), (0, "")),
		pytest.param(None, True, (1, "error"), (0, "")),
		pytest.param(None, True, (0, "success"), (0, "")),
		pytest.param(constants.DEVEL_BRANCHNAME, False, (1, "error"), (0, "")),
		pytest.param(constants.DEVEL_BRANCHNAME, False, (0, "success"), (0, "")),
		pytest.param(constants.DEVEL_BRANCHNAME, True, (1, "error"), (1, "error")),
		pytest.param(constants.DEVEL_BRANCHNAME, True, (0, "success"), (0, ""))
	],
	indirect=[
		"__mock_branch_exists_in_repo",
		"__mock_execute_git_command_for_source"
	]
)
def test_returns_expected_value_when_switching_branches(
	branch,
	__mock_branch_exists_in_repo,
	__mock_execute_git_command_for_source,
	expected_result
):
	result = ModeCompileAndInstallExecutor(
		{**__CONTEXT, __PARAM_BRANCH: branch}
	)._ModeCompileAndInstallExecutor__switch_branches()
	assert (
		result == expected_result
	), get_assertion_message("switch branches result", expected_result, result)

def test_calls_switch_branches_when_running_cmake_mode(
	__mock_switch_branches
):
	__mock_switch_branches.return_value = (1, "error")
	ModeCompileAndInstallExecutor(__CONTEXT.copy())._run_cmake_mode(__CMAKE)
	__mock_switch_branches.assert_called_once_with()

def test_does_not_call_logger_if_switching_branches_fails_when_running_cmake_mode(
	__mock_switch_branches,
	__mock_logger
):
	__mock_switch_branches.return_value = (1, "")
	ModeCompileAndInstallExecutor(__CONTEXT.copy())._run_cmake_mode(__CMAKE)
	__mock_logger.assert_not_called()

def test_calls_get_section_message_once_if_compilation_fails_when_running_cmake_mode(
	__mock_get_section_message,
	__mock_run_shell_command_in_streaming
):
	__mock_run_shell_command_in_streaming.return_value = 1
	ModeCompileAndInstallExecutor(__CONTEXT.copy())._run_cmake_mode(__CMAKE)
	__mock_get_section_message.assert_called_once_with("Compiling with CMake")

def test_calls_logger_once_if_compilation_fails(
	__mock_get_section_message,
	__mock_run_shell_command_in_streaming,
	__mock_logger
):
	__mock_run_shell_command_in_streaming.return_value = 1
	ModeCompileAndInstallExecutor(__CONTEXT.copy())._run_cmake_mode(__CMAKE)
	__mock_logger.assert_called_once_with(__mock_get_section_message("Compiling with CMake"))

@pytest.mark.parametrize(
	"keep_output", [pytest.param(False), pytest.param(True)]
)
def test_calls_run_shell_command_in_streaming_once_if_first_command_fails_when_running_cmake_mode(
	keep_output,
	__mock_run_shell_command_in_streaming,
	__mock_build_path,
	__mock_build_type
):
	__mock_run_shell_command_in_streaming.return_value = 1
	ModeCompileAndInstallExecutor(
		{**__CONTEXT, __PARAM_KEEP_OUTPUT: keep_output}
	)._run_cmake_mode(__CMAKE)
	__mock_run_shell_command_in_streaming.assert_called_once_with(
		f"{__CMAKE} --build {__mock_build_path} --config {__mock_build_type} -j {__N_JOBS}",
		show_output=True,
		substitute=not keep_output
	)

def test_calls_get_section_message_twice_if_first_command_succeeds_when_running_cmake_mode(
	__mock_get_section_message
):
	ModeCompileAndInstallExecutor(__CONTEXT.copy())._run_cmake_mode(__CMAKE)
	expected_calls = [
		call("Compiling with CMake"),
		call("Installing with CMake")
	]
	__mock_get_section_message.assert_has_calls(expected_calls)
	assert (
		__mock_get_section_message.call_count == len(expected_calls)
	), get_assertion_message(
		__CALL_COUNT_ASSERTION_MESSAGE,
		len(expected_calls),
		__mock_get_section_message.call_count
	)

def test_calls_logger_twice_if_first_command_succeeds_when_running_cmake_mode(
	__mock_get_section_message,
	__mock_logger
):
	ModeCompileAndInstallExecutor(__CONTEXT.copy())._run_cmake_mode(__CMAKE)
	expected_calls = [
		call(__mock_get_section_message("Compiling with CMake")),
		call("\n" + __mock_get_section_message("Installing with CMake"))
	]
	__mock_logger.assert_has_calls(expected_calls)
	assert (
		__mock_logger.call_count == len(expected_calls)
	), get_assertion_message(
		__CALL_COUNT_ASSERTION_MESSAGE,
		len(expected_calls),
		__mock_logger.call_count
	)

@pytest.mark.parametrize(
	"keep_output", [pytest.param(False), pytest.param(True)]
)
def test_calls_run_shell_command_in_streaming_twice_if_first_command_succeeds_when_running_cmake_mode(
	keep_output,
	__mock_run_shell_command_in_streaming,
	__mock_build_path,
	__mock_build_type
):
	ModeCompileAndInstallExecutor(
		{**__CONTEXT, __PARAM_KEEP_OUTPUT: keep_output}
	)._run_cmake_mode(__CMAKE)
	expected_calls = [
		call(
			f"{__CMAKE} --build {__mock_build_path} --config {__mock_build_type} -j {__N_JOBS}",
			show_output=True,
			substitute=not keep_output
		),
		call(
			f"{__CMAKE} --install {__mock_build_path} --config {__mock_build_type}",
			show_output=True,
			substitute=not keep_output
		)
	]
	__mock_run_shell_command_in_streaming.assert_has_calls(expected_calls)
	assert (
		__mock_run_shell_command_in_streaming.call_count == len(expected_calls)
	), get_assertion_message(
		__CALL_COUNT_ASSERTION_MESSAGE,
		len(expected_calls),
		__mock_run_shell_command_in_streaming.call_count
	)

@pytest.mark.parametrize(
	"__mock_switch_branches,__mock_run_shell_command_in_streaming,expected_output",
	[
		pytest.param((1, "error"), [1, 1], (1, "error"), id="Everything fails"),
		pytest.param((1, "error"), [0, 0], (1, "error"), id="Switch fails, both commands works"),
		pytest.param((0, ""), [1, 1], (errors.CMAKE_COMPILE_ERROR, ""), id="Switch works, both commands fails"),
		pytest.param((0, ""), [1, 0], (errors.CMAKE_COMPILE_ERROR, ""), id="Compile error"),
		pytest.param((0, ""), [0, 1], (errors.CMAKE_INSTALL_ERROR, ""), id="Install error"),
		pytest.param((0, ""), [0, 0], (0, ""), id="Success")
	],
	indirect=["__mock_switch_branches", "__mock_run_shell_command_in_streaming"]
)
def test_returns_expected_result_when_running_cmake_mode(
	__mock_switch_branches,
	__mock_run_shell_command_in_streaming,
	expected_output
):
	result = ModeCompileAndInstallExecutor(__CONTEXT.copy())._run_cmake_mode(__CMAKE)
	assert (
		result == expected_output
	), get_assertion_message("cmake mode result", expected_output, result)

@pytest.fixture
def __dummy_test_mode_cmake_executor():
	class TestExecutor(ModeCMakeExecutor):
		def _run_cmake_mode(self, _):
			return 0, ""
	TestExecutor(__CONTEXT.copy())._run_cmake_mode("") # For coverage
	return TestExecutor

@pytest.fixture(autouse=True)
def __mock_param_branch():
	with patch.object(
		params, "PARAM_BRANCH", __PARAM_BRANCH
	) as mock_object:
		yield mock_object

@pytest.fixture(autouse=True)
def __mock_param_keep_output():
	with patch.object(
		params, "PARAM_KEEP_OUTPUT", __PARAM_KEEP_OUTPUT
	) as mock_object:
		yield mock_object

@pytest.fixture(autouse=True)
def __mock_param_jobs():
	with patch.object(
		params, "PARAM_JOBS", __PARAM_JOBS
	) as mock_object:
		yield mock_object

@pytest.fixture(params=[(0, "")], autouse=True)
def __mock_mode_git_executor(request):
	mock_run = MagicMock()
	mock_run.return_value = request.param
	with patch(
		"xmipp3_installer.installer.modes.mode_git_executor.ModeGitExecutor"
  ) as mock_class:
		mock_class.return_value.run = mock_run
		yield mock_class

@pytest.fixture(autouse=True)
def __mock_param_git_command():
	with patch.object(
		params, "PARAM_GIT_COMMAND", __PARAM_GIT_COMMAND
	) as mock_object:
		yield mock_object

@pytest.fixture(params=[(0, "")])
def __mock_switch_branches(request):
	with patch(
		"xmipp3_installer.installer.modes.mode_cmake.mode_compile_and_install_executor.ModeCompileAndInstallExecutor._ModeCompileAndInstallExecutor__switch_branches"
	) as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_logger():
	with patch(
		"xmipp3_installer.application.logger.logger.Logger.__call__"
	) as mock_method:
		yield mock_method

@pytest.fixture
def __mock_get_section_message():
	with patch(
		"xmipp3_installer.application.logger.predefined_messages.get_section_message"
	) as mock_method:
		mock_method.side_effect = lambda text: f"section-{text}-section"
		yield mock_method

@pytest.fixture(params=[0], autouse=True)
def __mock_run_shell_command_in_streaming(request):
	with patch(
		"xmipp3_installer.installer.handlers.shell_handler.run_shell_command_in_streaming"
  ) as mock_method:
		if isinstance(request.param, int) == 1:
			mock_method.return_value = request.param
		else:
			mock_method.side_effect = request.param
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_build_path():
	with patch.object(
		paths, "BUILD_PATH", __BUILD_PATH
	) as mock_object:
		yield mock_object

@pytest.fixture(autouse=True)
def __mock_build_type():
	with patch.object(
		constants, "BUILD_TYPE", __BUILD_TYPE
	) as mock_object:
		yield mock_object

@pytest.fixture(params=[True], autouse=True)
def __mock_branch_exists_in_repo(request):
	with patch(
		"xmipp3_installer.installer.handlers.git_handler.branch_exists_in_repo"
	) as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(params=[(0, "")], autouse=True)
def __mock_execute_git_command_for_source(request):
	with patch(
		"xmipp3_installer.installer.handlers.git_handler.execute_git_command_for_source"
	) as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_logger_yellow():
  with patch(
    "xmipp3_installer.application.logger.logger.Logger.yellow"
  ) as mock_method:
    mock_method.side_effect = lambda text: f"yellow-{text}-yellow"
    yield mock_method
