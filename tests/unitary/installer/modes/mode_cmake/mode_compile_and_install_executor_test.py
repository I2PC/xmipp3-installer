from unittest.mock import patch, MagicMock, call

import pytest

from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.application.logger import errors
from xmipp3_installer.installer import constants, urls
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.installer.modes.mode_cmake.mode_cmake_executor import ModeCMakeExecutor
from xmipp3_installer.installer.modes.mode_cmake.mode_compile_and_install_executor import ModeCompileAndInstallExecutor
from xmipp3_installer.repository.config_vars import variables

from .... import DummyVersionsManager
from ..... import get_assertion_message

__CMAKE = "cmake_executable"
__PARAM_BRANCH = "branch_param"
__PARAM_KEEP_OUTPUT = "keep-output"
__PARAM_JOBS = "param_jobs"
__PARAM_GIT_COMMAND = "git_command"
__BUILD_PATH = "build_path"
__BUILD_TYPE = "build_type"
__CMAKE_KEY = "cmake_key"
__N_JOBS = 5
__CONTEXT = {
	__PARAM_BRANCH: None,
	constants.VERSIONS_CONTEXT_KEY: DummyVersionsManager(),
	__PARAM_KEEP_OUTPUT: False,
	__PARAM_JOBS: __N_JOBS,
	__BUILD_TYPE: "Release",
	__CMAKE_KEY: "/path/to/cmake"
}
__CALL_COUNT_ASSERTION_MESSAGE = "call count"
__COMPILING_MESSAGE = "Compiling with CMake"

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

def test_raises_key_error_if_param_jobs_not_in_context_when_initializing():
	new_context = __CONTEXT.copy()
	del new_context[__PARAM_JOBS]
	with pytest.raises(KeyError):
		ModeCompileAndInstallExecutor(new_context)

@pytest.mark.parametrize(
	"jobs",
	[pytest.param(None), pytest.param(__N_JOBS)]
)
def test_stores_expected_context_values_when_initializing(jobs):
	executor = ModeCompileAndInstallExecutor({
		**__CONTEXT, __PARAM_JOBS: jobs
	})
	assert (
		executor.jobs == jobs
	), get_assertion_message("stored jobs", jobs, executor.jobs)

def test_calls_get_section_message_once_if_compilation_fails_when_running_cmake_mode(
	__mock_get_section_message,
	__mock_run_shell_command_in_streaming
):
	__mock_run_shell_command_in_streaming.return_value = 1
	ModeCompileAndInstallExecutor(__CONTEXT.copy())._run_cmake_mode(__CMAKE)
	__mock_get_section_message.assert_called_once_with(__COMPILING_MESSAGE)

def test_calls_logger_once_if_compilation_fails(
	__mock_get_section_message,
	__mock_run_shell_command_in_streaming,
	__mock_logger
):
	__mock_run_shell_command_in_streaming.return_value = 1
	ModeCompileAndInstallExecutor(__CONTEXT.copy())._run_cmake_mode(__CMAKE)
	__mock_logger.assert_called_once_with(__mock_get_section_message(__COMPILING_MESSAGE))

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
		f"{__CMAKE} --build {__mock_build_path} --config {__CONTEXT[__mock_build_type]} -j {__N_JOBS}",
		show_output=True,
		substitute=not keep_output
	)

def test_calls_get_section_message_twice_if_first_command_succeeds_when_running_cmake_mode(
	__mock_get_section_message
):
	ModeCompileAndInstallExecutor(__CONTEXT.copy())._run_cmake_mode(__CMAKE)
	expected_calls = [
		call(__COMPILING_MESSAGE),
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
		call(__mock_get_section_message(__COMPILING_MESSAGE)),
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
			f"{__CMAKE} --build {__mock_build_path} --config {__CONTEXT[__mock_build_type]} -j {__N_JOBS}",
			show_output=True,
			substitute=not keep_output
		),
		call(
			f"{__CMAKE} --install {__mock_build_path} --config {__CONTEXT[__mock_build_type]}",
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
	"__mock_run_shell_command_in_streaming,expected_output",
	[
		pytest.param([1, 1], (errors.CMAKE_COMPILE_ERROR, ""), id="Both commands fails"),
		pytest.param([1, 0], (errors.CMAKE_COMPILE_ERROR, ""), id="Compile error"),
		pytest.param([0, 1], (errors.CMAKE_INSTALL_ERROR, ""), id="Install error"),
		pytest.param([0, 0], (0, ""), id="Success")
	],
	indirect=["__mock_run_shell_command_in_streaming"]
)
def test_returns_expected_result_when_running_cmake_mode(
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
		variables, "BUILD_TYPE", __BUILD_TYPE
	) as mock_object:
		yield mock_object

@pytest.fixture(autouse=True)
def __mock_cmake():
	with patch.object(
		variables, "CMAKE", __CMAKE_KEY
	) as mock_object:
		yield mock_object

@pytest.fixture(params=[(0, "")], autouse=True)
def __mock_execute_git_command_for_source(request):
	with patch(
		"xmipp3_installer.installer.handlers.git_handler.execute_git_command_for_source"
	) as mock_method:
		mock_method.return_value = request.param
		yield mock_method
