from unittest.mock import patch, MagicMock, call

import pytest

from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.installer.modes.mode_get_sources_executor import ModeGetSourcesExecutor
from xmipp3_installer.installer.modes.mode_executor import ModeExecutor
from xmipp3_installer.installer.modes.mode_all_executor import ModeAllExecutor
from xmipp3_installer.installer.modes.mode_config_executor import ModeConfigExecutor
from xmipp3_installer.installer.modes.mode_cmake.mode_config_build_executor import ModeConfigBuildExecutor
from xmipp3_installer.installer.modes.mode_cmake.mode_compile_and_install_executor import ModeCompileAndInstallExecutor

from .... import get_assertion_message

__PARAM_OVERWRITE = "param_overwrite"
__PARAM_BRANCH = "param_branch"
__DUMMY_CONTEXT = {"key": "value"}

def test_implements_interface_mode_cmake_executor():
	executor = ModeAllExecutor({})
	assert (
		isinstance(executor, ModeExecutor)
	), get_assertion_message(
		"parent class",
		ModeExecutor.__name__,
		executor.__class__.__bases__[0].__name__
	)

def test_overrides_expected_parent_config_values(__dummy_test_mode_cmake_executor):
	base_executor = __dummy_test_mode_cmake_executor({})
	executor = ModeAllExecutor({})
	base_config = (
		not base_executor.logs_to_file,
		not base_executor.prints_with_substitution,
		not base_executor.prints_banner_on_exit,
		not base_executor.sends_installation_info
	)
	inherited_config = (
		executor.logs_to_file,
		executor.prints_with_substitution,
		executor.prints_banner_on_exit,
		executor.sends_installation_info
	)
	assert (
		inherited_config == base_config
	), get_assertion_message("config values", base_config, inherited_config)

def test_calls_config_executor_when_initializing(__mock_config_executor):
	ModeAllExecutor(__DUMMY_CONTEXT)
	__mock_config_executor.assert_called_once_with(
		{**__DUMMY_CONTEXT, __PARAM_OVERWRITE: False}
	)

def test_calls_get_sources_executor_when_initializing(__mock_get_sources_executor):
	ModeAllExecutor(__DUMMY_CONTEXT)
	__mock_get_sources_executor.assert_called_once_with(__DUMMY_CONTEXT)

def test_calls_config_build_executor_when_initializing(__mock_config_build_executor):
	ModeAllExecutor(__DUMMY_CONTEXT)
	__mock_config_build_executor.assert_called_once_with(__DUMMY_CONTEXT)

def test_calls_compile_and_install_executor_when_initializing(__mock_compile_and_install_executor):
	ModeAllExecutor(__DUMMY_CONTEXT)
	__mock_compile_and_install_executor.assert_called_once_with(
		__DUMMY_CONTEXT
	)

def test_instantiates_expected_executors_when_initializing(
	__mock_config_executor,
	__mock_get_sources_executor,
	__mock_config_build_executor,
	__mock_compile_and_install_executor
):
	executor = ModeAllExecutor({})
	expected_executors = [
		__mock_config_executor(),
		__mock_get_sources_executor(),
		__mock_config_build_executor(),
		__mock_compile_and_install_executor()
	]
	assert (
		executor.executors == expected_executors
	), get_assertion_message("stored executors", expected_executors, executor.executors)

def test_calls_config_executor_run_when_running_executor(
	__mock_config_executor
):
	ModeAllExecutor({}).run()
	__mock_config_executor().run.assert_called_once_with()

def test_calls_get_sources_executor_run_if_config_executor_run_succeeds_when_running_executor(
	__mock_get_sources_executor
):
	ModeAllExecutor({}).run()
	__mock_get_sources_executor().run.assert_called_once_with()

def test_does_not_call_get_sources_executor_run_if_config_executor_run_fails_when_running_executor(
	__mock_config_executor,
	__mock_get_sources_executor
):
	__mock_config_executor().run.return_value = (1, "error")
	ModeAllExecutor({}).run()
	__mock_get_sources_executor().run.assert_not_called()

def test_calls_config_build_executor_run_if_config_get_sources_executor_run_succeed_when_running_executor(
	__mock_config_build_executor
):
	ModeAllExecutor({}).run()
	__mock_config_build_executor().run.assert_called_once_with()

@pytest.mark.parametrize(
	"__mock_config_executor,__mock_get_sources_executor",
	[
		pytest.param((0, ""), (1, "error")),
		pytest.param((1, "error"), (0, "")),
		pytest.param((1, "error"), (1, "error"))
	],
	indirect=True
)
def test_does_not_call_config_build_executor_run_if_config_or_get_sources_executor_run_fail_when_running_executor(
	__mock_config_executor,
	__mock_get_sources_executor,
	__mock_config_build_executor
):
	ModeAllExecutor({}).run()
	__mock_config_build_executor().run.assert_not_called()

def test_calls_compile_and_install_executor_run_if_other_executors_run_succeed_when_running_executor(
	__mock_compile_and_install_executor
):
	ModeAllExecutor({}).run()
	__mock_compile_and_install_executor().run.assert_called_once_with()

@pytest.mark.parametrize(
	"__mock_config_executor,__mock_get_sources_executor,__mock_config_build_executor",
	[
		pytest.param((0, ""), (0, ""), (1, "error")),
		pytest.param((0, ""), (1, "error"), (0, "")),
		pytest.param((0, ""), (1, "error"), (1, "error")),
		pytest.param((1, "error"), (0, ""), (0, "")),
		pytest.param((1, "error"), (0, ""), (1, "error")),
		pytest.param((1, "error"), (1, "error"), (0, "")),
		pytest.param((1, "error"), (1, "error"), (1, "error"))
	],
	indirect=True
)
def test_does_not_call_compile_and_install_executor_run_if_any_of_other_executors_run_fails_when_running_executor(
	__mock_config_executor,
	__mock_get_sources_executor,
	__mock_config_build_executor,
	__mock_compile_and_install_executor
):
	ModeAllExecutor({}).run()
	__mock_compile_and_install_executor().run.assert_not_called()

@pytest.mark.parametrize(
	"__mock_config_executor,__mock_get_sources_executor,"
	"__mock_config_build_executor,__mock_compile_and_install_executor,"
	"expected_call_number",
	[
		pytest.param((1, "error"), (1, "error"), (1, "error"), (1, "error"), 0),
		pytest.param((1, "error"), (1, "error"), (1, "error"), (0, ""), 0),
		pytest.param((1, "error"), (1, "error"), (0, ""), (1, "error"), 0),
		pytest.param((1, "error"), (1, "error"), (0, ""), (0, ""), 0),
		pytest.param((1, "error"), (0, ""), (1, "error"), (1, "error"), 0),
		pytest.param((1, "error"), (0, ""), (1, "error"), (0, ""), 0),
		pytest.param((1, "error"), (0, ""), (0, ""), (1, "error"), 0),
		pytest.param((1, "error"), (0, ""), (0, ""), (0, ""), 0),
		pytest.param((0, ""), (1, "error"), (1, "error"), (1, "error"), 1),
		pytest.param((0, ""), (1, "error"), (1, "error"), (0, ""), 1),
		pytest.param((0, ""), (1, "error"), (0, ""), (1, "error"), 1),
		pytest.param((0, ""), (1, "error"), (0, ""), (0, ""), 1),
		pytest.param((0, ""), (0, ""), (1, "error"), (1, "error"), 2),
		pytest.param((0, ""), (0, ""), (1, "error"), (0, ""), 2),
		pytest.param((0, ""), (0, ""), (0, ""), (1, "error"), 3),
		pytest.param((0, ""), (0, ""), (0, ""), (0, ""), 3)
	],
	indirect=[
		"__mock_config_executor",
		"__mock_get_sources_executor",
		"__mock_config_build_executor",
		"__mock_compile_and_install_executor"
	]
)
def test_calls_logger_expected_amount_of_times_when_running_executor(
	__mock_config_executor,
	__mock_get_sources_executor,
	__mock_config_build_executor,
	__mock_compile_and_install_executor,
	expected_call_number,
	__mock_logger
):
	ModeAllExecutor({}).run()
	expected_calls = [call("") for _ in range(expected_call_number)]
	__mock_logger.assert_has_calls(expected_calls)
	assert (
		__mock_logger.call_count == expected_call_number
	), get_assertion_message("call count", expected_call_number, __mock_logger.call_count)

@pytest.mark.parametrize(
	"__mock_config_executor,__mock_get_sources_executor,__mock_config_build_executor,"
	"__mock_compile_and_install_executor,expected_result",
	[
		pytest.param((1, "config"), (2, "sources"), (3, "config-build"), (4, "compile"), (1, "config")),
		pytest.param((1, "config"), (2, "sources"), (3, "config-build"), (0, "compile"), (1, "config")),
		pytest.param((1, "config"), (2, "sources"), (0, "config-build"), (4, "compile"), (1, "config")),
		pytest.param((1, "config"), (2, "sources"), (0, "config-build"), (0, "compile"), (1, "config")),
		pytest.param((1, "config"), (0, "sources"), (3, "config-build"), (4, "compile"), (1, "config")),
		pytest.param((1, "config"), (0, "sources"), (3, "config-build"), (0, "compile"), (1, "config")),
		pytest.param((1, "config"), (0, "sources"), (0, "config-build"), (4, "compile"), (1, "config")),
		pytest.param((1, "config"), (0, "sources"), (0, "config-build"), (0, "compile"), (1, "config")),
		pytest.param((0, "config"), (2, "sources"), (3, "config-build"), (4, "compile"), (2, "sources")),
		pytest.param((0, "config"), (2, "sources"), (3, "config-build"), (0, "compile"), (2, "sources")),
		pytest.param((0, "config"), (2, "sources"), (0, "config-build"), (4, "compile"), (2, "sources")),
		pytest.param((0, "config"), (2, "sources"), (0, "config-build"), (0, "compile"), (2, "sources")),
		pytest.param((0, "config"), (0, "sources"), (3, "config-build"), (4, "compile"), (3, "config-build")),
		pytest.param((0, "config"), (0, "sources"), (3, "config-build"), (0, "compile"), (3, "config-build")),
		pytest.param((0, "config"), (0, "sources"), (0, "config-build"), (4, "compile"), (4, "compile")),
		pytest.param((0, "config"), (0, "sources"), (0, "config-build"), (0, "compile"), (0, "")),
	],
	indirect=[
		"__mock_config_executor",
		"__mock_get_sources_executor",
		"__mock_config_build_executor",
		"__mock_compile_and_install_executor"
	]
)
def test_returns_expected_result_when_running_executor(
	__mock_config_executor,
	__mock_get_sources_executor,
	__mock_config_build_executor,
	__mock_compile_and_install_executor,
	expected_result
):
	result = ModeAllExecutor({}).run()
	assert (
		result == expected_result
	), get_assertion_message("executor run result", expected_result, result)

@pytest.fixture
def __dummy_test_mode_cmake_executor():
	class TestExecutor(ModeExecutor):
		def run(self):
			return 0, ""
	TestExecutor({}).run() # For coverage
	return TestExecutor

@pytest.fixture(params=[(0, "")], autouse=True)
def __mock_config_executor(request):
	executor = MagicMock(spec=ModeConfigExecutor)
	executor.run.return_value = request.param
	with patch(
		"xmipp3_installer.installer.modes.mode_config_executor.ModeConfigExecutor"
  ) as mock_class:
		mock_class.return_value = executor
		yield mock_class

@pytest.fixture(params=[(0, "")], autouse=True)
def __mock_get_sources_executor(request):
	executor = MagicMock(spec=ModeGetSourcesExecutor)
	executor.run.return_value = request.param
	with patch(
		"xmipp3_installer.installer.modes.mode_get_sources_executor.ModeGetSourcesExecutor"
  ) as mock_class:
		mock_class.return_value = executor
		yield mock_class

@pytest.fixture(params=[(0, "")], autouse=True)
def __mock_config_build_executor(request):
	executor = MagicMock(spec=ModeConfigBuildExecutor)
	executor.run.return_value = request.param
	with patch(
		"xmipp3_installer.installer.modes.mode_cmake.mode_config_build_executor.ModeConfigBuildExecutor"
  ) as mock_class:
		mock_class.return_value = executor
		yield mock_class

@pytest.fixture(params=[(0, "")], autouse=True)
def __mock_compile_and_install_executor(request):
	executor = MagicMock(spec=ModeCompileAndInstallExecutor)
	executor.run.return_value = request.param
	with patch(
		"xmipp3_installer.installer.modes.mode_cmake.mode_compile_and_install_executor.ModeCompileAndInstallExecutor"
  ) as mock_class:
		mock_class.return_value = executor
		yield mock_class

@pytest.fixture(autouse=True)
def __mock_param_overwrite():
	with patch.object(
		params, "PARAM_OVERWRITE", __PARAM_OVERWRITE
	) as mock_object:
		yield mock_object

@pytest.fixture(autouse=True)
def __mock_param_branch():
	with patch.object(
		params, "PARAM_BRANCH", __PARAM_BRANCH
	) as mock_object:
		yield mock_object

@pytest.fixture(autouse=True)
def __mock_logger():
	with patch(
		"xmipp3_installer.application.logger.logger.Logger.__call__"
	) as mock_method:
		yield mock_method
