import pytest
from unittest.mock import patch, call

from xmipp3_installer.installer import constants
from xmipp3_installer.installer.modes.mode_executor import ModeExecutor
from xmipp3_installer.installer.modes.mode_git_executor import ModeGitExecutor

from .... import get_assertion_message

__GIT_COMMAND_PARAMS = ["status", "-s"]
__GIT_COMMAND = "status -s"
__CONTEXT = {
	'command': __GIT_COMMAND_PARAMS
}
__RETURN_VALUES_STR = "return values"
__SOURCES = [constants.XMIPP, *constants.XMIPP_SOURCES]
__SOURCE_PATH = "source_path"
__CALL_COUNT_ASSERTION_MESSAGE = "call count"

def test_implements_interface_mode_executor():
	executor = ModeGitExecutor(__CONTEXT.copy())
	assert (
		isinstance(executor, ModeExecutor)
	), get_assertion_message(
		"parent class",
		ModeExecutor.__name__,
		executor.__class__.__bases__[0].__name__
	)

def test_sets_command_when_initializing():
	executor = ModeGitExecutor(__CONTEXT.copy())
	assert (
		executor.command == __GIT_COMMAND
	), get_assertion_message("git command", __GIT_COMMAND, executor.command)

def test_does_not_override_parent_config_values(
	__dummy_test_mode_executor
):
	base_executor = __dummy_test_mode_executor({})
	git_executor = ModeGitExecutor(__CONTEXT.copy())
	base_config = (
		base_executor.logs_to_file,
		base_executor.prints_with_substitution,
		base_executor.prints_banner_on_exit,
		base_executor.sends_installation_info
	)
	inherited_config = (
		git_executor.logs_to_file,
		git_executor.prints_with_substitution,
		git_executor.prints_banner_on_exit,
		git_executor.sends_installation_info
	)
	assert (
		inherited_config == base_config
	), get_assertion_message("config values", base_config, inherited_config)

def test_calls_logger_when_running_executor(
	__mock_logger,
	__mock_logger_blue,
	__mock_get_path_source
):
	executor = ModeGitExecutor(__CONTEXT.copy())
	executor.run()
	expected_calls = [
		call(f"Running command '{__GIT_COMMAND}' for all xmipp sources..."),
		*[
			call(
				"\n" + __mock_logger_blue(f"Running command for {source} in path {__mock_get_path_source(source)}...")
			) for source in __SOURCES
		]
	]
	__mock_logger.assert_has_calls(expected_calls)
	assert (
		__mock_logger.call_count == len(expected_calls)
	), get_assertion_message(
		__CALL_COUNT_ASSERTION_MESSAGE,
		len(expected_calls),
		__mock_logger.call_count
	)

def test_calls_execute_git_command_for_source_for_each_existing_source(
	__mock_execute_git_command_for_source
):
	ModeGitExecutor(__CONTEXT.copy()).run()
	expected_calls = [
		call(__GIT_COMMAND, source)
		for source in __SOURCES
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
	"__mock_execute_git_command_for_source,expected_return_values",
	[
		pytest.param((0, ""), (0, "")),
		pytest.param((0, "success"), (0, "")),
		pytest.param((1, "error"), (1, "error"))
	],
	indirect=["__mock_execute_git_command_for_source"]
)
def test_returns_expected_values_when_running_executor(
	__mock_execute_git_command_for_source,
	expected_return_values
):
	executor = ModeGitExecutor(__CONTEXT.copy())
	return_values = executor.run()
	assert (
		return_values == expected_return_values
	), get_assertion_message(__RETURN_VALUES_STR, expected_return_values, return_values)

@pytest.fixture
def __dummy_test_mode_executor():
	class TestExecutor(ModeExecutor):
		def run(self):
			return 0, ""
	TestExecutor(__CONTEXT.copy()).run() # For coverage
	return TestExecutor

@pytest.fixture(autouse=True)
def __mock_logger():
	with patch(
		"xmipp3_installer.application.logger.logger.Logger.__call__"
	) as mock_method:
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_logger_blue():
	with patch(
		"xmipp3_installer.application.logger.logger.Logger.blue"
	) as mock_method:
		mock_method.side_effect = lambda text: f"blue-{text}-blue"
		yield mock_method

@pytest.fixture(params=[(0, "")], autouse=True)
def __mock_execute_git_command_for_source(request):
	with patch(
		"xmipp3_installer.installer.handlers.git_handler.execute_git_command_for_source"
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
