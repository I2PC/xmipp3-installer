from unittest.mock import patch, call

import pytest

from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.application.logger import errors
from xmipp3_installer.installer import constants
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.installer.modes.mode_cmake import mode_config_build_executor
from xmipp3_installer.installer.modes.mode_cmake.mode_cmake_executor import ModeCMakeExecutor
from xmipp3_installer.installer.modes.mode_cmake.mode_config_build_executor import ModeConfigBuildExecutor
from xmipp3_installer.repository.config_vars import variables

from .... import DummyVersionsManager
from ..... import get_assertion_message

__PARAM_BRANCH = "branch_param"
__PARAM_KEEP_OUTPUT = "keep-output"
__INTERNAL_VARIABLE1 = "iternal1"
__INTERNAL_VARIABLE2 = "iternal2"
__VAR1_KEY = "section1_var1"
__VAR1_VALUE = "value1"
__VAR2_KEY = "section1_var2"
__VAR2_VALUE = "value2"
__VAR3_KEY = "section2var2"
__VAR3_VALUE = "value3"
__CONFIG_VARIABLES = {
  "section1": [
    __VAR1_KEY,__VAR2_KEY, __INTERNAL_VARIABLE1
  ],
  "section2": [
    __INTERNAL_VARIABLE2, __VAR3_KEY
  ]
}
__INTERNAL_VARIABLES = [__INTERNAL_VARIABLE1, __INTERNAL_VARIABLE2]
__NON_INTERNAL_VARIABLES = [__VAR1_KEY, __VAR2_KEY, __VAR3_KEY]
__CMAKE = "cmake_executable"
__SECTION_MESSAGE = "section message"
__CMAKE_VARS = f"-D{__VAR1_KEY}={__VAR1_VALUE} -D{__VAR2_KEY}={__VAR2_VALUE} -D{__VAR3_KEY}={__VAR3_VALUE}"
__BUILD_PATH = "build_path"
__BUILD_TYPE = "build_type"
__CMAKE = "cmake_key"
__CONTEXT = {
  __PARAM_BRANCH: constants.DEVEL_BRANCHNAME,
  constants.VERSIONS_CONTEXT_KEY: DummyVersionsManager(),
  __PARAM_KEEP_OUTPUT: False,
  __VAR1_KEY: __VAR1_VALUE,
  __VAR2_KEY: __VAR2_VALUE,
  __VAR3_KEY: __VAR3_VALUE,
  __BUILD_TYPE: "Release",
  __CMAKE: "/path/to/cmake"
}

def test_implements_interface_mode_cmake_executor():
  executor = ModeConfigBuildExecutor(__CONTEXT.copy())
  assert (
    isinstance(executor, ModeCMakeExecutor)
  ), get_assertion_message(
    "parent class",
    ModeCMakeExecutor.__name__,
    executor.__class__.__bases__[0].__name__
  )

def test_does_not_override_parent_config_values(__dummy_test_mode_cmake_executor):
  base_executor = __dummy_test_mode_cmake_executor(__CONTEXT.copy())
  config_build_executor = ModeConfigBuildExecutor(__CONTEXT.copy())
  base_config = (
    base_executor.logs_to_file,
    base_executor.prints_with_substitution,
    base_executor.prints_banner_on_exit,
    base_executor.sends_installation_info
  )
  inherited_config = (
    config_build_executor.logs_to_file,
    config_build_executor.prints_with_substitution,
    config_build_executor.prints_banner_on_exit,
    config_build_executor.sends_installation_info
  )
  assert (
    inherited_config == base_config
  ), get_assertion_message("config values", base_config, inherited_config)

@pytest.mark.parametrize(
  "input_value,expected_is_empty",
  [
    pytest.param("", True),
    pytest.param(None, True),
    pytest.param(False, False),
    pytest.param("something", False)
  ]
)
def test_returns_expected_is_empty_value(input_value, expected_is_empty):
  is_empty = mode_config_build_executor._is_empty(input_value)
  assert (
    is_empty == expected_is_empty
  ), get_assertion_message("is empty value", expected_is_empty, is_empty)

def test_returns_expected_config_vars():
  config_vars = mode_config_build_executor._get_non_internal_config_vars()
  config_vars.sort()
  expected_config_vars = __NON_INTERNAL_VARIABLES
  expected_config_vars.sort()
  assert (
    config_vars == expected_config_vars
  ), get_assertion_message("config variables", expected_config_vars, config_vars)

def test_calls_get_non_internal_config_vars_when_getting_cmake_vars(
  __mock_get_non_internal_config_vars
):
  ModeConfigBuildExecutor(__CONTEXT.copy())._ModeConfigBuildExecutor__get_cmake_vars()
  __mock_get_non_internal_config_vars.assert_called_once_with()

@pytest.mark.parametrize(
  "__mock_get_non_internal_config_vars,expected_cmake_vars",
  [
    pytest.param([], ""),
    pytest.param(__NON_INTERNAL_VARIABLES, __CMAKE_VARS)
  ],
  indirect=["__mock_get_non_internal_config_vars"]
)
def test_returns_expected_cmake_vars(__mock_get_non_internal_config_vars, expected_cmake_vars):
  cmake_vars = ModeConfigBuildExecutor(__CONTEXT.copy())._ModeConfigBuildExecutor__get_cmake_vars()
  assert (
    cmake_vars == expected_cmake_vars
  ), get_assertion_message("CMake variables", expected_cmake_vars, cmake_vars)

def test_calls_get_section_message_when_running_cmake_mode(
  __mock_get_section_message,
  __mock_get_cmake_vars
):
  ModeConfigBuildExecutor(__CONTEXT.copy())._run_cmake_mode(__CMAKE)
  __mock_get_section_message.assert_called_once_with("Configuring with CMake")

def test_calls_logger_once_if_command_fails_when_running_cmake_mode(
  __mock_logger,
  __mock_get_section_message,
  __mock_get_cmake_vars,
  __mock_run_shell_command_in_streaming
):
  __mock_run_shell_command_in_streaming.return_value = 1
  ModeConfigBuildExecutor(__CONTEXT.copy())._run_cmake_mode(__CMAKE)
  __mock_logger.assert_called_once_with(__mock_get_section_message())

@pytest.mark.parametrize(
  "substitute",
  [pytest.param(False), pytest.param(True)]
)
def test_calls_logger_twice_if_command_succeeds_when_running_cmake_mode(
  substitute,
  __mock_logger,
  __mock_get_section_message,
  __mock_get_done_message,
  __mock_get_cmake_vars
):
  executor = ModeConfigBuildExecutor(__CONTEXT.copy())
  executor.substitute = substitute
  executor._run_cmake_mode(__CMAKE)
  expected_calls = [
    call(__mock_get_section_message()),
    call(__mock_get_done_message(), substitute=substitute)
  ]
  __mock_logger.assert_has_calls(expected_calls)
  assert (
    __mock_logger.call_count == len(expected_calls)
  ), get_assertion_message(
    "call count",
    len(expected_calls),
    __mock_logger.call_count
  )

@pytest.mark.parametrize(
  "keep_output", [pytest.param(False), pytest.param(True)]
)
def test_calls_run_shell_command_in_streaming_when_running_cmake_mode(
  keep_output,
  __mock_get_cmake_vars,
  __mock_run_shell_command_in_streaming,
  __mock_build_path,
  __mock_build_type
):
  ModeConfigBuildExecutor(
    {**__CONTEXT, __PARAM_KEEP_OUTPUT: keep_output}
  )._run_cmake_mode(__CMAKE)
  __mock_run_shell_command_in_streaming.assert_called_once_with(
    f"{__CMAKE} -S . -B {__mock_build_path} -DCMAKE_BUILD_TYPE={__CONTEXT[__mock_build_type]} {__mock_get_cmake_vars()}",
    show_output=True,
    substitute=not keep_output
  )

@pytest.mark.parametrize(
  "__mock_run_shell_command_in_streaming",
  [pytest.param(1), pytest.param(2)],
  indirect=["__mock_run_shell_command_in_streaming"]
)
def test_calls_get_error_code_if_command_fails_when_running_cmake_mode(
  __mock_run_shell_command_in_streaming,
  __mock_get_error_code
):
  ModeConfigBuildExecutor(
    __CONTEXT.copy()
  )._run_cmake_mode(__CMAKE)
  __mock_get_error_code.assert_called_once_with(
    __mock_run_shell_command_in_streaming(),
    errors.CMAKE_CONFIGURE_ERROR
  )

def test_does_not_call_get_error_code_if_command_succeeds_when_running_cmake_mode(
  __mock_get_error_code
):
  ModeConfigBuildExecutor(
    __CONTEXT.copy()
  )._run_cmake_mode(__CMAKE)
  __mock_get_error_code.assert_not_called()

@pytest.mark.parametrize(
  "__mock_run_shell_command_in_streaming,__mock_get_error_code,expected_output",
  [
    pytest.param(1, 5, (5, "")),
    pytest.param(1, 1, (1, "")),
    pytest.param(0, 5, (0, "")),
    pytest.param(0, 1, (0, ""))
  ],
  indirect=[
    "__mock_run_shell_command_in_streaming",
    "__mock_get_error_code"
  ]
)
def test_reurns_expected_result_when_running_cmake_mode(
  __mock_run_shell_command_in_streaming,
  __mock_get_error_code,
  expected_output,
  __mock_get_cmake_vars
):
  result = ModeConfigBuildExecutor(__CONTEXT.copy())._run_cmake_mode(__CMAKE)
  assert (
    result == expected_output
  ), get_assertion_message("CMake mode output", expected_output, result)

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
def __mock_config_variables():
  with patch.object(
    variables, "CONFIG_VARIABLES", __CONFIG_VARIABLES
  ) as mock_object:
    yield mock_object

@pytest.fixture(autouse=True)
def __mock_internal_logic_vars():
  with patch.object(
    variables, "INTERNAL_LOGIC_VARS", __INTERNAL_VARIABLES
  ) as mock_object:
    yield mock_object

@pytest.fixture(params=[__NON_INTERNAL_VARIABLES])
def __mock_get_non_internal_config_vars(request):
  with patch(
    "xmipp3_installer.installer.modes.mode_cmake.mode_config_build_executor._get_non_internal_config_vars"
  ) as mock_method:
    mock_method.return_value = request.param
    yield mock_method

@pytest.fixture(autouse=True)
def __mock_logger():
  with patch(
    "xmipp3_installer.application.logger.logger.Logger.__call__"
  ) as mock_method:
    yield mock_method

@pytest.fixture(autouse=True)
def __mock_get_section_message():
  with patch(
    "xmipp3_installer.application.logger.predefined_messages.get_section_message"
  ) as mock_method:
    mock_method.return_value = __SECTION_MESSAGE
    yield mock_method

@pytest.fixture
def __mock_get_done_message():
  with patch(
    "xmipp3_installer.application.logger.predefined_messages.get_done_message"
  ) as mock_method:
    mock_method.return_value = "done message"
    yield mock_method

@pytest.fixture(params=[0], autouse=True)
def __mock_run_shell_command_in_streaming(request):
  with patch(
    "xmipp3_installer.installer.handlers.shell_handler.run_shell_command_in_streaming"
  ) as mock_method:
    mock_method.return_value = request.param
    yield mock_method

@pytest.fixture
def __mock_get_cmake_vars():
  with patch(
    "xmipp3_installer.installer.modes.mode_cmake.mode_config_build_executor.ModeConfigBuildExecutor._ModeConfigBuildExecutor__get_cmake_vars"
  ) as mock_method:
    mock_method.return_value = __CMAKE_VARS
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
    variables, "CMAKE", __CMAKE
  ) as mock_object:
    yield mock_object

@pytest.fixture(params=[1])
def __mock_get_error_code(request):
  with patch(
    "xmipp3_installer.installer.modes.mode_cmake.mode_cmake_executor.ModeCMakeExecutor._get_error_code"
  ) as mock_method:
    mock_method.return_value = request.param
    yield mock_method
