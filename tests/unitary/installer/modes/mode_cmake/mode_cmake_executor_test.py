from unittest.mock import patch

import pytest

from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.application.logger import errors
from xmipp3_installer.installer.modes.mode_executor import ModeExecutor
from xmipp3_installer.installer.modes.mode_cmake.mode_cmake_executor import ModeCMakeExecutor
from xmipp3_installer.repository.config_vars import variables

from ..... import get_assertion_message

__CMAKE = "/path/to/cmake"
__BUILD_TYPE = "build_type"
__CONTEXT = {
  params.PARAM_KEEP_OUTPUT: False,
  variables.CMAKE: __CMAKE,
  variables.BUILD_TYPE: __BUILD_TYPE
}
__CMAKE_ERROR_MESSAGE = "CMake installation not found."

def test_implements_interface_mode_executor(__dummy_test_mode_cmake_executor):
  cmake_executor = __dummy_test_mode_cmake_executor(__CONTEXT.copy())
  assert (
    isinstance(cmake_executor, ModeExecutor)
  ), get_assertion_message(
    "parent class",
    ModeExecutor.__name__,
    cmake_executor.__class__.__bases__[0].__name__
  )

def test_raises_exception_when_run_method_not_implemented(
  __no_implementation_child
):
  with pytest.raises(TypeError):
    __no_implementation_child({})

def test_overrides_expected_parent_config_values(
  __dummy_test_mode_cmake_executor,
  __dummy_test_mode_executor
):
  base_executor = __dummy_test_mode_executor({})
  cmake_executor = __dummy_test_mode_cmake_executor(__CONTEXT.copy())
  base_config = (
    not base_executor.logs_to_file,
    not base_executor.prints_with_substitution,
    base_executor.prints_banner_on_exit,
    base_executor.sends_installation_info
  )
  inherited_config = (
    cmake_executor.logs_to_file,
    cmake_executor.prints_with_substitution,
    cmake_executor.prints_banner_on_exit,
    cmake_executor.sends_installation_info
  )
  assert (
    inherited_config == base_config
  ), get_assertion_message("config values", base_config, inherited_config)

@pytest.mark.parametrize(
  "variable_name",
  [pytest.param(variables.CMAKE), pytest.param(variables.BUILD_TYPE)]
)
def test_raises_key_error_if_variable_not_present_in_context_when_initializing(
  variable_name,
  __dummy_test_mode_cmake_executor
):
  new_context = __CONTEXT.copy()
  del new_context[variable_name]
  with pytest.raises(KeyError):
    __dummy_test_mode_cmake_executor(new_context)

@pytest.mark.parametrize(
  "keep_output", [pytest.param(False), pytest.param(True)]
)
def test_stores_expected_values_when_initializing(
  __dummy_test_mode_cmake_executor,
  keep_output
):
  executor = __dummy_test_mode_cmake_executor(
    {**__CONTEXT, params.PARAM_KEEP_OUTPUT: keep_output}
  )
  values = (
    executor.substitute,
    executor.cmake,
    executor.build_type
  )
  expected_values = (
    not keep_output,
    __CMAKE,
    __BUILD_TYPE
  )
  assert (
    values == expected_values
  ), get_assertion_message("stored values", expected_values, values)

def test_calls_get_cmake_path_if_cmake_in_context_not_valid_when_getting_cmake_executable(
  __dummy_test_mode_cmake_executor,
  __mock_get_cmake_path
):
  __dummy_test_mode_cmake_executor(
    {**__CONTEXT, variables.CMAKE: None}
  )._ModeCMakeExecutor__get_cmake_executable()
  __mock_get_cmake_path.assert_called_once_with()

def test_does_not_call_get_cmake_path_if_cmake_in_context_valid_when_getting_cmake_executable(
  __dummy_test_mode_cmake_executor,
  __mock_get_cmake_path
):
  __dummy_test_mode_cmake_executor(
    __CONTEXT.copy()
  )._ModeCMakeExecutor__get_cmake_executable()
  __mock_get_cmake_path.assert_not_called()

@pytest.mark.parametrize(
  "cmake_in_context,__mock_get_cmake_path,expected_cmake_path",
  [
    pytest.param(None, None, None),
    pytest.param(None, __CMAKE, __CMAKE),
    pytest.param(__CMAKE, None, __CMAKE),
    pytest.param(__CMAKE, "other_path", __CMAKE)
  ],
  indirect=["__mock_get_cmake_path"]
)
def test_returns_expected_cmake_path(
  cmake_in_context,
  __mock_get_cmake_path,
  expected_cmake_path,
  __dummy_test_mode_cmake_executor
):
  cmake_path = __dummy_test_mode_cmake_executor(
    {**__CONTEXT, variables.CMAKE: cmake_in_context}
  )._ModeCMakeExecutor__get_cmake_executable()
  assert (
    cmake_path == expected_cmake_path
  ), get_assertion_message("CMake path", expected_cmake_path, cmake_path)

@pytest.mark.parametrize(
  "ret_code,mode_error_code,expected_error_code",
  [
    pytest.param(errors.INTERRUPTED_ERROR, errors.INTERRUPTED_ERROR, errors.INTERRUPTED_ERROR),
    pytest.param(errors.INTERRUPTED_ERROR, errors.CMAKE_COMPILE_ERROR, errors.INTERRUPTED_ERROR),
    pytest.param(errors.CMAKE_COMPILE_ERROR, errors.CMAKE_COMPILE_ERROR, errors.CMAKE_COMPILE_ERROR),
    pytest.param(errors.CMAKE_COMPILE_ERROR, errors.CMAKE_CONFIGURE_ERROR, errors.CMAKE_CONFIGURE_ERROR)
  ]
)
def test_returns_expected_error_code(
  ret_code,
  mode_error_code,
  expected_error_code,
  __dummy_test_mode_cmake_executor
):
  error_code = __dummy_test_mode_cmake_executor(
    __CONTEXT.copy()
  )._get_error_code(ret_code, mode_error_code)
  assert (
    error_code == expected_error_code
  ), get_assertion_message("error code", expected_error_code, error_code)

def test_calls_get_cmake_executable_when_running_executor(
  __dummy_test_mode_cmake_executor,
  __mock_get_cmake_executable
):
  __mock_get_cmake_executable.return_value = None
  __dummy_test_mode_cmake_executor(__CONTEXT.copy()).run()
  __mock_get_cmake_executable.assert_called_once_with()

@pytest.mark.parametrize(
  "__mock_get_cmake_executable,cmake_mode_result,expected_output",
  [
    pytest.param(None, (1, "failure"), (errors.CMAKE_ERROR, __CMAKE_ERROR_MESSAGE)),
    pytest.param(None, (0, "success"), (errors.CMAKE_ERROR, __CMAKE_ERROR_MESSAGE)),
    pytest.param(__CMAKE, (1, "failure"), (1, "failure")),
    pytest.param(__CMAKE, (0, "success"), (0, "success"))
  ],
  indirect=["__mock_get_cmake_executable"]
)
def test_returns_expected_result_when_running_executor(
  __mock_get_cmake_executable,
  cmake_mode_result,
  expected_output,
  __dummy_test_mode_cmake_executor
):
  class ModifiableDummyCMakeExecutor(__dummy_test_mode_cmake_executor):
    def _run_cmake_mode(self, _):
      return cmake_mode_result
  ret_code, output = ModifiableDummyCMakeExecutor(__CONTEXT.copy()).run()
  assert (
    (ret_code, output) == expected_output
  ), get_assertion_message(
    "model operation output",
    expected_output,
    (ret_code, output)
  )

@pytest.fixture
def __no_implementation_child():
  class DummyModeExecutor(ModeCMakeExecutor):
    pass
  return DummyModeExecutor

@pytest.fixture
def __dummy_test_mode_cmake_executor():
  class TestExecutor(ModeCMakeExecutor):
    def _run_cmake_mode(self, _):
      return 0, ""
  TestExecutor(__CONTEXT.copy())._run_cmake_mode("") # For coverage
  return TestExecutor

@pytest.fixture
def __dummy_test_mode_executor():
  class TestExecutor(ModeExecutor):
    def run(self):
      return 0, ""
  TestExecutor({}).run() # For coverage
  return TestExecutor

@pytest.fixture(params=[__CMAKE], autouse=True)
def __mock_get_cmake_path(request):
  with patch("xmipp3_installer.installer.handlers.cmake.cmake_handler.get_cmake_path") as mock_method:
    mock_method.return_value = request.param
    yield mock_method

@pytest.fixture(params=[__CMAKE])
def __mock_get_cmake_executable(request):
  with patch(
    "xmipp3_installer.installer.modes.mode_cmake.mode_cmake_executor.ModeCMakeExecutor._ModeCMakeExecutor__get_cmake_executable"
  ) as mock_method:
    mock_method.return_value = request.param
    yield mock_method
