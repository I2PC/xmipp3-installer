from unittest.mock import patch, call

import pytest

from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.application.logger import errors
from xmipp3_installer.installer import constants, urls
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.installer.modes import mode_get_sources_executor
from xmipp3_installer.installer.modes.mode_executor import ModeExecutor
from xmipp3_installer.installer.modes.mode_get_sources_executor import ModeGetSourcesExecutor

from ... import DummyVersionsManager
from .... import (
  JSON_XMIPP_VERSION_NAME, get_assertion_message,
  JSON_XMIPP_CORE_TARGET_TAG, JSON_XMIPP_VIZ_TARGET_TAG
)

__PARAM_BRANCH = "branch_param"
__PARAM_KEEP_OUTPUT = "keep-output"
__CONTEXT = {
  __PARAM_BRANCH: constants.MAIN_BRANCHNAME,
  constants.VERSIONS_CONTEXT_KEY: DummyVersionsManager(),
  __PARAM_KEEP_OUTPUT: False
}
__BRANCH_NAME = "test_branch"
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
__I2PC_REPOSITORY_URL = "i2pc_repository_url"
__XMIPP_SOURCES = ["source1", "source2"]

def test_implements_interface_mode_executor():
  executor = ModeGetSourcesExecutor(__CONTEXT.copy())
  assert (
    isinstance(executor, ModeExecutor)
  ), get_assertion_message(
    "parent class",
    ModeExecutor.__name__,
    executor.__class__.__bases__[0].__name__
  )

def test_overrides_expected_parent_config_values(__dummy_test_mode_executor):
  base_executor = __dummy_test_mode_executor(__CONTEXT.copy())
  get_sources_executor = ModeGetSourcesExecutor(__CONTEXT.copy())
  base_config = (
    base_executor.logs_to_file,
    not base_executor.prints_with_substitution,
    base_executor.prints_banner_on_exit,
    base_executor.sends_installation_info
  )
  inherited_config = (
    get_sources_executor.logs_to_file,
    get_sources_executor.prints_with_substitution,
    get_sources_executor.prints_banner_on_exit,
    get_sources_executor.sends_installation_info
  )
  assert (
    inherited_config == base_config
  ), get_assertion_message("config values", base_config, inherited_config)

def test_stores_expected_values_when_initializing():
  executor = ModeGetSourcesExecutor(__CONTEXT.copy())
  values = (
    executor.substitute,
    executor.target_branch,
    executor.xmipp_tag_name,
    executor.source_versions
  )
  expected_values = (
    True,
    constants.MAIN_BRANCHNAME,
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
  [
    pytest.param(__PARAM_KEEP_OUTPUT),
    pytest.param(__PARAM_BRANCH),
    pytest.param(constants.VERSIONS_CONTEXT_KEY)
  ]
)
def test_raises_key_error_if_variable_not_present_in_context_when_initializing(
  variable_key
):
  context = __CONTEXT.copy()
  del context[variable_key]
  with pytest.raises(KeyError):
    ModeGetSourcesExecutor(context)

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
    pytest.param(constants.XMIPP_CORE, __CONTEXT[constants.VERSIONS_CONTEXT_KEY].xmipp_version_name, __EXISTING_TAG),
    pytest.param(constants.XMIPP_CORE, constants.MAIN_BRANCHNAME, None),
    pytest.param(constants.XMIPP_CORE, __BRANCH_NAME, None),
    pytest.param(__NON_EXISTING_SOURCE, None, None),
    pytest.param(__NON_EXISTING_SOURCE, constants.MAIN_BRANCHNAME, None),
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
  mode_get_sources_executor._run_source_command(
    constants.XMIPP_VIZ, __REPO_URL, __BRANCH_NAME
  )
  __mock_get_source_path.assert_called_once_with(constants.XMIPP_VIZ)

def test_calls_os_path_exists_when_running_source_command(
  __mock_get_source_path,
  __mock_os_path_exists
):
  mode_get_sources_executor._run_source_command(
    constants.XMIPP_CORE, __REPO_URL, __BRANCH_NAME
  )
  __mock_os_path_exists.assert_called_once_with(
    __mock_get_source_path(constants.XMIPP_CORE)
  )

def test_does_not_call_run_shell_command_if_source_exists_and_target_branch_does_not_when_running_source_command(
  __mock_run_shell_command
):
  mode_get_sources_executor._run_source_command(
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
  mode_get_sources_executor._run_source_command(
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
  mode_get_sources_executor._run_source_command(
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
  result = mode_get_sources_executor._run_source_command(
    constants.XMIPP_CORE, __REPO_URL, target_branch
  )
  assert (
    result == expected_result
  ), get_assertion_message("result", expected_result, result)

@pytest.mark.parametrize(
  "target_branch,source_name,__mock_select_ref_to_clone,"
  "__mock_run_source_command,substitute",
  [
    pytest.param(None, constants.XMIPP_CORE, None, (0, ""), False),
    pytest.param(None, constants.XMIPP_CORE, None, (0, ""), True),
    pytest.param(None, constants.XMIPP_CORE, None, (1, "error"), False),
    pytest.param(None, constants.XMIPP_CORE, None, (1, "error"), True),
    pytest.param(None, constants.XMIPP_CORE, __BRANCH_NAME, (0, ""), False),
    pytest.param(None, constants.XMIPP_CORE, __BRANCH_NAME, (0, ""), True),
    pytest.param(None, constants.XMIPP_CORE, __BRANCH_NAME, (1, "error"), False),
    pytest.param(None, constants.XMIPP_CORE, __BRANCH_NAME, (1, "error"), True),
    pytest.param(None, constants.XMIPP_VIZ, None, (0, ""), False),
    pytest.param(None, constants.XMIPP_VIZ, None, (0, ""), True),
    pytest.param(None, constants.XMIPP_VIZ, None, (1, "error"), False),
    pytest.param(None, constants.XMIPP_VIZ, None, (1, "error"), True),
    pytest.param(None, constants.XMIPP_VIZ, __BRANCH_NAME, (0, ""), False),
    pytest.param(None, constants.XMIPP_VIZ, __BRANCH_NAME, (0, ""), True),
    pytest.param(None, constants.XMIPP_VIZ, __BRANCH_NAME, (1, "error"), False),
    pytest.param(None, constants.XMIPP_VIZ, __BRANCH_NAME, (1, "error"), True),
    pytest.param(__BRANCH_NAME, constants.XMIPP_CORE, None, (0, ""), False),
    pytest.param(__BRANCH_NAME, constants.XMIPP_CORE, None, (0, ""), True),
    pytest.param(__BRANCH_NAME, constants.XMIPP_CORE, None, (1, "error"), False),
    pytest.param(__BRANCH_NAME, constants.XMIPP_CORE, None, (1, "error"), True),
    pytest.param(__BRANCH_NAME, constants.XMIPP_CORE, __BRANCH_NAME, (0, ""), False),
    pytest.param(__BRANCH_NAME, constants.XMIPP_CORE, __BRANCH_NAME, (0, ""), True),
    pytest.param(__BRANCH_NAME, constants.XMIPP_CORE, __BRANCH_NAME, (1, "error"), False),
    pytest.param(__BRANCH_NAME, constants.XMIPP_CORE, __BRANCH_NAME, (1, "error"), True),
    pytest.param(__BRANCH_NAME, constants.XMIPP_VIZ, None, (0, ""), False),
    pytest.param(__BRANCH_NAME, constants.XMIPP_VIZ, None, (0, ""), True),
    pytest.param(__BRANCH_NAME, constants.XMIPP_VIZ, None, (1, "error"), False),
    pytest.param(__BRANCH_NAME, constants.XMIPP_VIZ, None, (1, "error"), True),
    pytest.param(__BRANCH_NAME, constants.XMIPP_VIZ, __BRANCH_NAME, (0, ""), False),
    pytest.param(__BRANCH_NAME, constants.XMIPP_VIZ, __BRANCH_NAME, (0, ""), True),
    pytest.param(__BRANCH_NAME, constants.XMIPP_VIZ, __BRANCH_NAME, (1, "error"), False),
    pytest.param(__BRANCH_NAME, constants.XMIPP_VIZ, __BRANCH_NAME, (1, "error"), True)
  ],
  indirect=["__mock_select_ref_to_clone", "__mock_run_source_command"]
)
def test_calls_logger_when_getting_source(
  target_branch,
  source_name,
  __mock_select_ref_to_clone,
  __mock_run_source_command,
  substitute,
  __mock_logger,
  __mock_logger_yellow,
  __mock_get_working_message,
  __mock_get_done_message,
  __mock_i2pc_repo_url
):
  ModeGetSourcesExecutor(
    {**__CONTEXT, __PARAM_BRANCH: target_branch, __PARAM_KEEP_OUTPUT: not substitute},
  )._ModeGetSourcesExecutor__get_source(source_name)
  expected_calls = [
    call(f"Cloning {source_name}...", substitute=substitute),
    call(__mock_get_working_message(), substitute=substitute),
  ]
  if target_branch and not __mock_select_ref_to_clone():
    expected_calls.append(
      call(
        "\n".join([
          __mock_logger_yellow(f"Warning: branch \'{target_branch}\' does not exist for repository with url {__mock_i2pc_repo_url}{source_name}"),
          __mock_logger_yellow("Falling back to repository's default branch.")
        ]),
        substitute=substitute
      )
    )
  if not __mock_run_source_command()[0]:
    expected_calls.append(
      call(__mock_get_done_message(), substitute=substitute)
    )
  __mock_logger.assert_has_calls(expected_calls)
  assert (
    __mock_logger.call_count == len(expected_calls)
  ), get_assertion_message("call count", len(expected_calls), __mock_logger.call_count)

def test_calls_get_working_message_when_getting_source(
  __mock_get_working_message,
  __mock_select_ref_to_clone,
  __mock_run_source_command
):
  ModeGetSourcesExecutor(__CONTEXT.copy())._ModeGetSourcesExecutor__get_source(
    constants.XMIPP_CORE
  )
  __mock_get_working_message.assert_called_once_with()

@pytest.mark.parametrize(
  "source_name",
  [pytest.param(constants.XMIPP_CORE), pytest.param(constants.XMIPP_VIZ)]
)
def test_calls_select_ref_to_clone_when_getting_source(
  source_name,
  __mock_select_ref_to_clone,
  __mock_run_source_command,
  __mock_i2pc_repo_url
):
  ModeGetSourcesExecutor(__CONTEXT.copy())._ModeGetSourcesExecutor__get_source(
    source_name
  )
  __mock_select_ref_to_clone.assert_called_once_with(
    source_name, f"{__mock_i2pc_repo_url}{source_name}"
  )

@pytest.mark.parametrize(
  "source_name,__mock_select_ref_to_clone",
  [
    pytest.param(constants.XMIPP_CORE, None),
    pytest.param(constants.XMIPP_CORE, __BRANCH_NAME),
    pytest.param(constants.XMIPP_VIZ, None),
    pytest.param(constants.XMIPP_VIZ, __BRANCH_NAME)
  ],
  indirect=["__mock_select_ref_to_clone"]
)
def test_calls_run_source_command_when_getting_source(
  source_name,
  __mock_select_ref_to_clone,
  __mock_run_source_command,
  __mock_i2pc_repo_url
):
  ModeGetSourcesExecutor(__CONTEXT.copy())._ModeGetSourcesExecutor__get_source(
    source_name
  )
  __mock_run_source_command.assert_called_once_with(
    source_name,
    f"{__mock_i2pc_repo_url}{source_name}",
    __mock_select_ref_to_clone()
  )

def test_calls_get_done_message_when_getting_source(
  __mock_get_done_message,
  __mock_select_ref_to_clone,
  __mock_run_source_command
):
  ModeGetSourcesExecutor(__CONTEXT.copy())._ModeGetSourcesExecutor__get_source(
    constants.XMIPP_CORE
  )
  __mock_get_done_message.assert_called_once_with()

@pytest.mark.parametrize(
  "__mock_run_source_command",
  [
    pytest.param((1, "error")),
    pytest.param((0, ""))
  ],
  indirect=["__mock_run_source_command"]
)
def test_returns_expected_result_when_getting_source(
  __mock_select_ref_to_clone,
  __mock_run_source_command
):
  result = ModeGetSourcesExecutor(__CONTEXT.copy())._ModeGetSourcesExecutor__get_source(
    constants.XMIPP_CORE
  )
  assert (
    result == __mock_run_source_command()
  ), get_assertion_message("result", __mock_run_source_command(), result)

def test_calls_logger_when_running_executor(
  __mock_logger,
  __mock_get_section_message,
  __mock_get_source
):
  ModeGetSourcesExecutor(__CONTEXT.copy()).run()
  __mock_logger.assert_called_once_with(
    __mock_get_section_message("Getting Xmipp sources")
  )

def test_calls_get_source_when_running_executor(
  __mock_xmipp_sources,
  __mock_get_source
):
  ModeGetSourcesExecutor(__CONTEXT.copy()).run()
  expected_calls = [
    call(source) for source in __mock_xmipp_sources
  ]
  __mock_get_source.assert_has_calls(expected_calls)
  assert (
    __mock_get_source.call_count == len(expected_calls)
  ), get_assertion_message("call count", len(expected_calls), __mock_get_source.call_count)

@pytest.mark.parametrize(
  "__mock_get_source,expected_result",
  [
    pytest.param((1, "error"), (errors.SOURCE_CLONE_ERROR, "error")),
    pytest.param((0, "success"), (0, ""))
  ],
  indirect=["__mock_get_source"]
)
def test_returns_expected_result_when_running_executor(
  __mock_get_source,
  expected_result
):
  result = ModeGetSourcesExecutor(__CONTEXT.copy()).run()
  assert (
    result == expected_result
  ), get_assertion_message("executor result", expected_result, result)

@pytest.fixture
def __dummy_test_mode_executor():
  class TestExecutor(ModeExecutor):
    def run(self):
      return 0, ""
  TestExecutor(__CONTEXT.copy()).run() # For coverage
  return TestExecutor

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
def __mock_param_keep_output():
  with patch.object(
    params, "PARAM_KEEP_OUTPUT", __PARAM_KEEP_OUTPUT
  ) as mock_object:
    yield mock_object

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
def __mock_get_working_message():
  with patch(
    "xmipp3_installer.application.logger.predefined_messages.get_working_message"
  ) as mock_method:
    mock_method.return_value = "working message"
    yield mock_method

@pytest.fixture(autouse=True)
def __mock_get_done_message():
  with patch(
    "xmipp3_installer.application.logger.predefined_messages.get_done_message"
  ) as mock_method:
    mock_method.return_value = "done message"
    yield mock_method

@pytest.fixture(params=[__BRANCH_NAME])
def __mock_select_ref_to_clone(request):
  with patch(
    "xmipp3_installer.installer.modes.mode_get_sources_executor.ModeGetSourcesExecutor._ModeGetSourcesExecutor__select_ref_to_clone"
  ) as mock_method:
    mock_method.return_value = request.param
    yield mock_method

@pytest.fixture(params=[(0, "")])
def __mock_run_source_command(request):
  with patch(
    "xmipp3_installer.installer.modes.mode_get_sources_executor._run_source_command"
  ) as mock_method:
    mock_method.return_value = request.param
    yield mock_method

@pytest.fixture(autouse=True)
def __mock_i2pc_repo_url():
  with patch.object(
    urls, "I2PC_REPOSITORY_URL", __I2PC_REPOSITORY_URL
  ) as mock_object:
    yield mock_object

@pytest.fixture(autouse=True)
def __mock_get_section_message():
  with patch(
    "xmipp3_installer.application.logger.predefined_messages.get_section_message"
  ) as mock_method:
    mock_method.side_effect = lambda text: f"section-{text}-section"
    yield mock_method

@pytest.fixture(params=[(0, "")])
def __mock_get_source(request):
  with patch(
    "xmipp3_installer.installer.modes.mode_get_sources_executor.ModeGetSourcesExecutor._ModeGetSourcesExecutor__get_source"
  ) as mock_method:
    mock_method.return_value = request.param
    yield mock_method

@pytest.fixture(autouse=True)
def __mock_xmipp_sources():
  with patch.object(
    constants, "XMIPP_SOURCES", __XMIPP_SOURCES
  ) as mock_object:
    yield mock_object
