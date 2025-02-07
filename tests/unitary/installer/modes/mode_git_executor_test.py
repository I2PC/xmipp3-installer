import pytest
from unittest.mock import patch, call

from xmipp3_installer.installer import constants
from xmipp3_installer.installer.modes.mode_executor import ModeExecutor
from xmipp3_installer.installer.modes.mode_git_executor import ModeGitExecutor

from .... import get_assertion_message

__GIT_COMMAND_PARAMS = "status -s"
__GIT_COMMAND = f"git {__GIT_COMMAND_PARAMS}"
__ARGS = {
	'git-command': __GIT_COMMAND_PARAMS
}
__RETURN_VALUES_STR = "return values"

def test_implements_interface_mode_executor():
	executor = ModeGitExecutor(__ARGS.copy())
	assert (
		isinstance(executor, ModeExecutor)
	), get_assertion_message(
		"parent class",
		ModeExecutor.__name__,
		executor.__class__.__bases__[0].__name__
	)

def test_sets_command_when_initializing():
	executor = ModeGitExecutor(__ARGS.copy())
	assert (
		executor.command == __GIT_COMMAND_PARAMS
	), get_assertion_message("git command", __GIT_COMMAND_PARAMS, executor.command)

def test_does_not_override_parent_config_values(
	__dummy_test_mode_executor
):
	base_executor = __dummy_test_mode_executor({})
	base_executor.run()  # To cover dummy implementation execution
	git_executor = ModeGitExecutor(__ARGS.copy())
	base_config = (
		base_executor.logs_to_file,
		base_executor.prints_with_substitution,
		base_executor.prints_banner_on_exit
	)
	inherited_config = (
		git_executor.logs_to_file,
		git_executor.prints_with_substitution,
		git_executor.prints_banner_on_exit
	)
	assert (
		inherited_config == base_config
	), get_assertion_message("config values", base_config, inherited_config)

def test_calls_logger_when_running_executor(__mock_logger):
	executor = ModeGitExecutor(__ARGS.copy())
	executor.run()
	__mock_logger.assert_has_calls([
		call(f"Running command '{__GIT_COMMAND}' for all xmipp sources..."),
		call("")
	])

def test_calls_os_path_abspath_for_each_source(__mock_os_path_abspath):
	executor = ModeGitExecutor(__ARGS.copy())
	executor.run()
	calls = []
	for source in constants.XMIPP_SOURCES:
		source_path = f"{constants.SOURCES_PATH}/{source}"
		calls.append(call(source_path))
	__mock_os_path_abspath.assert_has_calls(calls)
	assert (
		__mock_os_path_abspath.call_count == len(calls)
	), get_assertion_message("call count", len(calls), __mock_os_path_abspath.call_count)

def test_calls_os_path_exists_for_each_source(
	__mock_os_path_exists,
	__mock_run_shell_command
):
	ModeGitExecutor(__ARGS.copy()).run()
	calls = []
	for source in constants.XMIPP_SOURCES:
		source_path = f"abs-{constants.SOURCES_PATH}/{source}-abs"
		calls.append(call(source_path))
	__mock_os_path_exists.assert_has_calls(calls)
	assert (
		__mock_os_path_exists.call_count == len(calls)
	), get_assertion_message("call count", len(calls), __mock_os_path_exists.call_count)

def test_calls_logger_when_source_does_not_exist(
	__mock_logger,
	__mock_logger_yellow,
	__mock_os_path_exists
):
	__mock_os_path_exists.return_value = False
	executor = ModeGitExecutor(__ARGS.copy())
	executor.run()
	calls = [call(f"Running command 'git {__GIT_COMMAND_PARAMS}' for all xmipp sources...")]
	for source in constants.XMIPP_SOURCES:
		source_path = f"abs-{constants.SOURCES_PATH}/{source}-abs"
		calls.extend([
			call(""),
			call(__mock_logger_yellow(
				f"WARNING: Source {source} does not exist in path {source_path}. Skipping."
			))
		])
	__mock_logger.assert_has_calls(calls)

def test_calls_logger_when_source_exists(
	__mock_os_path_exists,
	__mock_logger,
	__mock_logger_blue,
	__mock_run_shell_command
):
	executor = ModeGitExecutor(__ARGS.copy())
	executor.run()
	calls = [call(f"Running command 'git {__GIT_COMMAND_PARAMS}' for all xmipp sources...")]
	for source in constants.XMIPP_SOURCES:
		source_path = f"abs-{constants.SOURCES_PATH}/{source}-abs"
		calls.extend([
			call(""),
			call(__mock_logger_blue(
				f"Running command for {source} in path {source_path}..."
			))
		])
	__mock_logger.assert_has_calls(calls)

def test_calls_run_shell_command_for_each_existing_source(
	__mock_os_path_exists,
	__mock_run_shell_command
):
	ModeGitExecutor(__ARGS.copy()).run()
	calls = []
	for source in constants.XMIPP_SOURCES:
		source_path = f"abs-{constants.SOURCES_PATH}/{source}-abs"
		calls.append(call(
			__GIT_COMMAND,
			cwd=source_path,
			show_output=True,
			show_error=True
		))
	__mock_run_shell_command.assert_has_calls(calls)

@pytest.mark.parametrize(
	"__mock_run_shell_command,expected_return_values",
	[
		pytest.param((0, ""), (0, "")),
		pytest.param((1, "error"), (1, "error"))
	],
	indirect=["__mock_run_shell_command"]
)
def test_returns_expected_values_when_running_executor(
	__mock_run_shell_command,
	expected_return_values,
	__mock_os_path_exists
):
	executor = ModeGitExecutor(__ARGS.copy())
	return_values = executor.run()
	assert (
		return_values == expected_return_values
	), get_assertion_message(__RETURN_VALUES_STR, expected_return_values, return_values)

def test_execute_git_command_for_source_when_source_does_not_exist(
	__mock_os_path_exists,
	__mock_logger,
	__mock_logger_yellow
):
	__mock_os_path_exists.return_value = False
	executor = ModeGitExecutor(__ARGS.copy())
	source = constants.XMIPP_SOURCES[0]
	ret_code, output = executor._ModeGitExecutor__execute_git_command_for_source(
		source,
		__GIT_COMMAND
	)
	
	source_path = f"abs-{constants.SOURCES_PATH}/{source}-abs"
	__mock_logger.assert_called_once_with(__mock_logger_yellow(
		f"WARNING: Source {source} does not exist in path {source_path}. Skipping."
	))
	assert ret_code == 0
	assert output == ""

def test_execute_git_command_for_source_when_source_exists(
	__mock_os_path_exists,
	__mock_logger,
	__mock_logger_blue,
	__mock_run_shell_command
):
	executor = ModeGitExecutor(__ARGS.copy())
	source = constants.XMIPP_SOURCES[0]
	expected_return = (0, "success")
	__mock_run_shell_command.return_value = expected_return
	
	ret_code, output = executor._ModeGitExecutor__execute_git_command_for_source(
		source,
		__GIT_COMMAND
	)
	
	source_path = f"abs-{constants.SOURCES_PATH}/{source}-abs"
	__mock_logger.assert_called_once_with(__mock_logger_blue(
		f"Running command for {source} in path {source_path}..."
	))
	__mock_run_shell_command.assert_called_once_with(
		__GIT_COMMAND,
		cwd=source_path,
		show_output=True,
		show_error=True
	)
	assert (ret_code, output) == expected_return

@pytest.fixture
def __dummy_test_mode_executor():
	class TestExecutor(ModeExecutor):
		def run(self):
			return (0, "")
	return TestExecutor

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

@pytest.fixture(autouse=True)
def __mock_logger_blue():
	with patch(
		"xmipp3_installer.application.logger.logger.Logger.blue"
	) as mock_method:
		mock_method.side_effect = lambda text: f"blue-{text}-blue"
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_os_path_join():
	with patch("os.path.join") as mock_method:
		mock_method.side_effect = lambda *args: '/'.join([*args])
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_os_path_abspath():
	with patch("os.path.abspath") as mock_method:
		mock_method.side_effect = lambda path: f"abs-{path}-abs"
		yield mock_method

@pytest.fixture(params=[True])
def __mock_os_path_exists(request):
	with patch("os.path.exists") as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(params=[(0, "")])
def __mock_run_shell_command(request):
	with patch(
		"xmipp3_installer.installer.handlers.shell_handler.run_shell_command"
	) as mock_method:
		mock_method.return_value = request.param
		yield mock_method
