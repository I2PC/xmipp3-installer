from unittest.mock import patch

import pytest

from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.installer import constants
from xmipp3_installer.installer.modes.mode_executor import ModeExecutor
from xmipp3_installer.installer.modes.mode_get_sources_executor import ModeGetSourcesExecutor

from ... import DummyVersionsManager
from .... import (
	JSON_XMIPP_VERSION_NAME, get_assertion_message,
	JSON_XMIPP_CORE_TARGET_TAG, JSON_XMIPP_VIZ_TARGET_TAG
)

__CONTEXT = {
	params.PARAM_BRANCH: constants.DEVEL_BRANCHNAME,
	constants.VERSIONS_CONTEXT_KEY: DummyVersionsManager()
}
__BRANCH_NAME = "devel"
__REPO_URL = "repourl"
__NON_EXISTING_SOURCE = "non_existing_source"
__EXISTING_TAG = __CONTEXT[constants.VERSIONS_CONTEXT_KEY].sources_versions[constants.XMIPP_CORE]

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
	[pytest.param(params.PARAM_BRANCH), pytest.param(constants.VERSIONS_CONTEXT_KEY)]
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
