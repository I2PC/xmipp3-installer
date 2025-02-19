import pytest

from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.installer import constants
from xmipp3_installer.installer.modes.mode_get_sources_executor import ModeGetSourcesExecutor

from .... import JSON_XMIPP_VERSION_NAME, get_assertion_message

class DummyVersionsManager:
  def __init__(self):
    self.xmipp_version_name = JSON_XMIPP_VERSION_NAME

__CONTEXT = {
  params.PARAM_BRANCH: constants.DEVEL_BRANCHNAME,
  constants.VERSIONS_CONTEXT_KEY: DummyVersionsManager()
}

def test_stores_expected_values_when_initializing():
  executor = ModeGetSourcesExecutor(__CONTEXT.copy())
  values = (
    executor.target_branch,
    executor.xmipp_tag_name
  )
  expected_values = (
    constants.DEVEL_BRANCHNAME,
    JSON_XMIPP_VERSION_NAME
  )
  assert (
    values == expected_values
  ), get_assertion_message("stored values", expected_values, values)

def test_raises_key_error_if_branch_not_present_in_context_when_initializing():
  context = __CONTEXT.copy()
  del context[params.PARAM_BRANCH]
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
