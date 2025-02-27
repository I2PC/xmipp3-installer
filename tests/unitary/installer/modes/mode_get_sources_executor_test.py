from unittest.mock import patch

import pytest

from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.installer import constants
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.installer.modes.mode_executor import ModeExecutor
from xmipp3_installer.installer.modes.mode_get_sources_executor import ModeGetSourcesExecutor

from ... import DummyVersionsManager
from .... import (
	JSON_XMIPP_VERSION_NAME, get_assertion_message,
	JSON_XMIPP_CORE_TARGET_TAG, JSON_XMIPP_VIZ_TARGET_TAG
)

__PARAM_BRANCH = "branch_param"
__CONTEXT = {
	__PARAM_BRANCH: constants.DEVEL_BRANCHNAME,
	constants.VERSIONS_CONTEXT_KEY: DummyVersionsManager()
}
__BRANCH_NAME = "devel"
__REPO_URL = "repourl"
__NON_EXISTING_SOURCE = "non_existing_source"
__EXISTING_TAG = __CONTEXT[constants.VERSIONS_CONTEXT_KEY].sources_versions[constants.XMIPP_CORE]
__LONG_VERSION = "long_version"
__PARAMS = {
	__PARAM_BRANCH: {
		__LONG_VERSION: "long_version"
	}
}
__SOURCES_PATH = "sources_path"

def test_implements_interface_mode_executor():
	executor = ModeGetSourcesExecutor(__CONTEXT.copy())
	assert (
		isinstance(executor, ModeExecutor)
	), get_assertion_message(
		"parent class",
		ModeExecutor.__name__,
		executor.__class__.__bases__[0].__name__
	)

def test_stores_expected_values_when_initializing():
	executor = ModeGetSourcesExecutor(__CONTEXT.copy())
	values = (
		executor.target_branch,
		executor.xmipp_tag_name,
		executor.source_versions
	)
	expected_values = (
		constants.DEVEL_BRANCHNAME,
		JSON_XMIPP_VERSION_NAME,
		{
			constants.XMIPP_CORE: JSON_XMIPP_CORE_TARGET_TAG,
			constants.XMIPP_VIZ: JSON_XMIPP_VIZ_TARGET_TAG
		}
	)
	assert (
		values == expected_values
	), get_assertion_message("stored values", expected_values, values)

@pytest.mark.parametrize(
	"variable_key",
	[pytest.param(__PARAM_BRANCH), pytest.param(constants.VERSIONS_CONTEXT_KEY)]
)
def test_raises_key_error_if_variable_not_present_in_context_when_initializing(
	variable_key
):
	context = __CONTEXT.copy()
	del context[variable_key]
	with pytest.raises(KeyError):
		ModeGetSourcesExecutor(context)

def test_sets_substitute_to_false_when_not_provided():
	executor = ModeGetSourcesExecutor(__CONTEXT.copy())
	assert (
		not executor.substitute
	), get_assertion_message("substitute default value", False, executor.substitute)

@pytest.mark.parametrize("expected_value", [pytest.param(False), pytest.param(True)])
def test_sets_substitute_value_when_provided(expected_value):
	executor = ModeGetSourcesExecutor(__CONTEXT.copy(), substitute=expected_value)
	assert (
		executor.substitute == expected_value
	), get_assertion_message("substitute value", expected_value, executor.substitute)

def test_calls_get_current_branch_when_selecting_ref_to_clone(
	__mock_get_current_branch
):
	ModeGetSourcesExecutor(__CONTEXT.copy())._ModeGetSourcesExecutor__select_ref_to_clone(
		constants.XMIPP_CORE, __REPO_URL
	)
	__mock_get_current_branch.assert_called_once_with()

@pytest.mark.parametrize(
	"source_name,__mock_get_current_branch,expected_tag_name",
	[
		pytest.param(constants.XMIPP_CORE, None, __EXISTING_TAG),
		pytest.param(constants.XMIPP_CORE, constants.MASTER_BRANCHNAME, __EXISTING_TAG),
		pytest.param(constants.XMIPP_CORE, __CONTEXT[constants.VERSIONS_CONTEXT_KEY].xmipp_version_name, __EXISTING_TAG),
		pytest.param(constants.XMIPP_CORE, __BRANCH_NAME, None),
		pytest.param(__NON_EXISTING_SOURCE, None, None),
		pytest.param(__NON_EXISTING_SOURCE, constants.MASTER_BRANCHNAME, None),
		pytest.param(__NON_EXISTING_SOURCE, __CONTEXT[constants.VERSIONS_CONTEXT_KEY].xmipp_version_name, None),
		pytest.param(__NON_EXISTING_SOURCE, __BRANCH_NAME, None),
	],
	indirect=["__mock_get_current_branch"]
)
def test_calls_get_clonable_branch_when_selecting_ref_to_clone(
	source_name,
	__mock_get_current_branch,
	expected_tag_name,
	__mock_get_clonable_branch
):
	ModeGetSourcesExecutor(__CONTEXT.copy())._ModeGetSourcesExecutor__select_ref_to_clone(
		source_name, __REPO_URL
	)
	__mock_get_clonable_branch.assert_called_once_with(
		__REPO_URL, __CONTEXT[params.PARAM_BRANCH], expected_tag_name
	)

@pytest.mark.parametrize(
	"__mock_get_clonable_branch",
	[pytest.param((0, "success")), pytest.param((1, "error"))],
	indirect=["__mock_get_clonable_branch"]
)
def test_returns_expected_ref_to_clone(__mock_get_clonable_branch):
	result = ModeGetSourcesExecutor(__CONTEXT.copy())._ModeGetSourcesExecutor__select_ref_to_clone(
		constants.XMIPP_CORE, __REPO_URL
	)
	assert (
		result == __mock_get_clonable_branch()
	), get_assertion_message("result", __mock_get_clonable_branch(), result)

def test_calls_get_source_path_when_running_source_command(
	__mock_get_source_path
):
	ModeGetSourcesExecutor(__CONTEXT.copy())._ModeGetSourcesExecutor__run_source_command(
		constants.XMIPP_VIZ, __REPO_URL, __BRANCH_NAME
	)
	__mock_get_source_path.assert_called_once_with(constants.XMIPP_VIZ)

def test_calls_os_path_exists_when_running_source_command(
	__mock_get_source_path,
	__mock_os_path_exists
):
	ModeGetSourcesExecutor(__CONTEXT.copy())._ModeGetSourcesExecutor__run_source_command(
		constants.XMIPP_CORE, __REPO_URL, __BRANCH_NAME
	)
	__mock_os_path_exists.assert_called_once_with(
		__mock_get_source_path(constants.XMIPP_CORE)
	)

def test_does_not_call_run_shell_command_if_source_exists_and_target_branch_does_not_when_running_source_command(
	__mock_run_shell_command
):
	ModeGetSourcesExecutor(__CONTEXT.copy())._ModeGetSourcesExecutor__run_source_command(
		constants.XMIPP_CORE, __REPO_URL, None
	)
	__mock_run_shell_command.assert_not_called()

@pytest.mark.parametrize(
	"source,target_branch",
	[
		pytest.param(constants.XMIPP_CORE, __BRANCH_NAME),
		pytest.param(constants.XMIPP_CORE, "random"),
		pytest.param(constants.XMIPP_VIZ, __BRANCH_NAME),
		pytest.param(constants.XMIPP_VIZ, "random")
	]
)
def test_calls_run_shell_command_if_source_and_target_branch_exist_when_running_source_command(
	source,
	target_branch,
	__mock_get_source_path,
	__mock_run_shell_command
):
	ModeGetSourcesExecutor(__CONTEXT.copy())._ModeGetSourcesExecutor__run_source_command(
		source, __REPO_URL, target_branch
	)
	__mock_run_shell_command.assert_called_once_with(
		f"git checkout {target_branch}",
		cwd=__mock_get_source_path(source)
	)

@pytest.mark.parametrize(
	"target_branch,expected_branch_str",
	[
		pytest.param(None, ""),
		pytest.param(__BRANCH_NAME, f"{__PARAMS[__PARAM_BRANCH][__LONG_VERSION]} {__BRANCH_NAME}")
	]
)
def test_calls_run_shell_command_if_source_does_not_exist_when_running_source_command(
	target_branch,
	expected_branch_str,
	__mock_os_path_exists,
	__mock_run_shell_command,
	__mock_sources_path
):
	__mock_os_path_exists.return_value = False
	ModeGetSourcesExecutor(__CONTEXT.copy())._ModeGetSourcesExecutor__run_source_command(
		constants.XMIPP_CORE, __REPO_URL, target_branch
	)
	__mock_run_shell_command.assert_called_once_with(
		f"git clone{expected_branch_str} {__REPO_URL}.git",
		cwd=__mock_sources_path
	)

@pytest.mark.parametrize(
	"__mock_os_path_exists,target_branch,"
	"__mock_run_shell_command,expected_result",
	[
		pytest.param(False, None, (1, "error"), (1, "error")),
		pytest.param(False, None, (0, "success"), (0, "success")),
		pytest.param(False, __BRANCH_NAME, (1, "error"), (1, "error")),
		pytest.param(False, __BRANCH_NAME, (0, "success"), (0, "success")),
		pytest.param(True, None, (1, "error"), (0, "")),
		pytest.param(True, None, (0, "success"), (0, "")),
		pytest.param(True, __BRANCH_NAME, (1, "error"), (1, "error")),
		pytest.param(True, __BRANCH_NAME, (0, "success"), (0, "success"))
	],
	indirect=["__mock_os_path_exists", "__mock_run_shell_command"]
)
def test_returns_expected_result_when_running_source_command(
	__mock_os_path_exists,
	target_branch,
	__mock_run_shell_command,
	expected_result
):
	result = ModeGetSourcesExecutor(__CONTEXT.copy())._ModeGetSourcesExecutor__run_source_command(
		constants.XMIPP_CORE, __REPO_URL, target_branch
	)
	assert (
		result == expected_result
	), get_assertion_message("result", expected_result, result)

@pytest.fixture(params=[__BRANCH_NAME])
def __mock_get_current_branch(request):
	with patch(
		"xmipp3_installer.installer.handlers.git_handler.get_current_branch"
	) as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(params=[__BRANCH_NAME], autouse=True)
def __mock_get_clonable_branch(request):
	with patch(
		"xmipp3_installer.installer.handlers.git_handler.get_clonable_branch"
	) as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_get_source_path():
	with patch(
		"xmipp3_installer.installer.constants.paths.get_source_path"
	) as mock_method:
		mock_method.side_effect = lambda source: f"sources/{source}"
		yield mock_method

@pytest.fixture(params=[True], autouse=True)
def __mock_os_path_exists(request):
	with patch("os.path.exists") as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(params=[(0, "")], autouse=True)
def __mock_run_shell_command(request):
  with patch(
    "xmipp3_installer.installer.handlers.shell_handler.run_shell_command"
  ) as mock_method:
    mock_method.return_value = request.param
    yield mock_method

@pytest.fixture(autouse=True)
def __mock_param_branch():
	with patch.object(
		params, "PARAM_BRANCH", __PARAM_BRANCH
	) as mock_object:
		yield mock_object

@pytest.fixture(autouse=True)
def __mock_long_version():
	with patch.object(
		params, "LONG_VERSION", __LONG_VERSION
	) as mock_object:
		yield mock_object

@pytest.fixture(autouse=True)
def __mock_params():
	with patch.object(
		params, "PARAMS", __PARAMS
	) as mock_object:
		yield mock_object

@pytest.fixture(autouse=True)
def __mock_sources_path():
	with patch.object(
		paths, "SOURCES_PATH", __SOURCES_PATH
	) as mock_object:
		yield mock_object
