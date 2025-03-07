from unittest.mock import patch, MagicMock

import pytest

from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.installer import constants
from xmipp3_installer.installer.modes.mode_get_sources_executor import ModeGetSourcesExecutor
from xmipp3_installer.installer.modes.mode_executor import ModeExecutor
from xmipp3_installer.installer.modes.mode_all_executor import ModeAllExecutor
from xmipp3_installer.installer.modes.mode_cmake.mode_config_build_executor import ModeConfigBuildExecutor
from xmipp3_installer.installer.modes.mode_cmake.mode_compile_and_install_executor import ModeCompileAndInstallExecutor

from ... import DummyVersionsManager
from .... import get_assertion_message

__PARAM_BRANCH = "branch_param"
__PARAM_KEEP_OUTPUT = "keep-output"
__PARAM_JOBS = "param_jobs"
__N_JOBS = 5
__CONTEXT = {
	__PARAM_BRANCH: None,
	constants.VERSIONS_CONTEXT_KEY: DummyVersionsManager(),
	__PARAM_KEEP_OUTPUT: False,
	__PARAM_JOBS: __N_JOBS
}

def test_implements_interface_mode_cmake_executor():
	executor = ModeAllExecutor(__CONTEXT.copy())
	assert (
		isinstance(executor, ModeExecutor)
	), get_assertion_message(
		"parent class",
		ModeExecutor.__name__,
		executor.__class__.__bases__[0].__name__
	)

def test_overrides_expected_parent_config_values(__dummy_test_mode_cmake_executor):
	base_executor = __dummy_test_mode_cmake_executor(__CONTEXT.copy())
	executor = ModeAllExecutor(__CONTEXT.copy())
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

@pytest.mark.parametrize(
	"missing_param",
	[pytest.param(__PARAM_BRANCH), pytest.param(__PARAM_JOBS)]
)
def test_raises_key_error_if_params_not_in_context_when_initializing(missing_param):
	new_context = __CONTEXT.copy()
	del new_context[missing_param]
	with pytest.raises(KeyError):
		ModeAllExecutor(new_context)

def test_instantiates_expected_executors(
	__mock_get_sources_executor,
	__mock_config_build_executor,
	__mock_compile_and_install_executor
):
	executor = ModeAllExecutor(__CONTEXT.copy())
	executors = (
		executor.get_sources_executor,
		executor.config_build_executor,
		executor.compile_and_install_executor
	)
	expected_executors = (
		__mock_get_sources_executor(),
		__mock_config_build_executor(),
		__mock_compile_and_install_executor()
	)
	assert (
		executors == expected_executors
	), get_assertion_message("stored executors", expected_executors, executors)

def test_calls_get_sources_executor_run_when_running_executor(
	__mock_get_sources_executor
):
	ModeAllExecutor(__CONTEXT.copy()).run()
	__mock_get_sources_executor().run.assert_called_once_with()

def test_calls_config_build_executor_run_if_get_sources_executor_run_succeeds_when_running_executor(
	__mock_config_build_executor
):
	ModeAllExecutor(__CONTEXT.copy()).run()
	__mock_config_build_executor().run.assert_called_once_with()

def test_does_not_call_config_build_executor_run_if_get_sources_executor_run_fails_when_running_executor(
	__mock_get_sources_executor,
	__mock_config_build_executor
):
	__mock_get_sources_executor().run.return_value = (1, "error")
	ModeAllExecutor(__CONTEXT.copy()).run()
	__mock_config_build_executor().run.assert_not_called()

def test_calls_compile_and_install_executor_run_if_other_executors_run_succeed_when_running_executor(
	__mock_compile_and_install_executor
):
	ModeAllExecutor(__CONTEXT.copy()).run()
	__mock_compile_and_install_executor().run.assert_called_once_with()

@pytest.mark.parametrize(
	"__mock_get_sources_executor,__mock_config_build_executor",
	[
		pytest.param((0, "error"), (1, "error")),
		pytest.param((1, "error"), (0, "")),
		pytest.param((1, "error"), (1, "error"))
	],
	indirect=True
)
def test_does_not_call_compile_and_install_executor_run_if_any_of_other_executors_run_fails_when_running_executor(
	__mock_get_sources_executor,
	__mock_config_build_executor,
	__mock_compile_and_install_executor
):
	ModeAllExecutor(__CONTEXT.copy()).run()
	__mock_compile_and_install_executor().run.assert_not_called()

@pytest.mark.parametrize(
	"__mock_get_sources_executor,__mock_config_build_executor,"
	"__mock_compile_and_install_executor,expected_result",
	[
		pytest.param((1, "sources"), (2, "config"), (3, "compile"), (1, "sources")),
		pytest.param((1, "sources"), (2, "config"), (0, "compile"), (1, "sources")),
		pytest.param((1, "sources"), (0, "config"), (3, "compile"), (1, "sources")),
		pytest.param((1, "sources"), (0, "config"), (0, "compile"), (1, "sources")),
		pytest.param((0, "sources"), (2, "config"), (3, "compile"), (2, "config")),
		pytest.param((0, "sources"), (2, "config"), (0, "compile"), (2, "config")),
		pytest.param((0, "sources"), (0, "config"), (3, "compile"), (3, "compile")),
		pytest.param((0, "sources"), (0, "config"), (0, "compile"), (0, ""))
	],
	indirect=[
		"__mock_get_sources_executor",
		"__mock_config_build_executor",
		"__mock_compile_and_install_executor"
	]
)
def test_returns_expected_result_when_running_executor(
	__mock_get_sources_executor,
	__mock_config_build_executor,
	__mock_compile_and_install_executor,
	expected_result
):
	result = ModeAllExecutor(__CONTEXT.copy()).run()
	assert (
		result == expected_result
	), get_assertion_message("executor run result", expected_result, result)

@pytest.fixture
def __dummy_test_mode_cmake_executor():
	class TestExecutor(ModeExecutor):
		def run(self):
			return 0, ""
	TestExecutor(__CONTEXT.copy()).run() # For coverage
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
