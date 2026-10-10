import json
from unittest.mock import patch, call

import pytest

from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.application.logger import errors
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.installer.modes import mode_conda_dependencies_executor
from xmipp3_installer.installer.modes.mode_conda_dependencies_executor import ModeCondaDependenciesExecutor
from xmipp3_installer.installer.modes.mode_executor import ModeExecutor
from xmipp3_installer.repository.config_vars import variables

from .... import get_assertion_message

__CONTEXT = {
  params.PARAM_KEEP_OUTPUT: False,
  variables.CUDA: True,
  variables.CONDA_ENVIRONMENT: None
}
__CONDA_EXECUTABLE = "/path/to/conda/bin/conda"
__CONDA_PREFIX = "/path/to/conda/envs/xmipp"
__SECTION_MESSAGE = "section message"
__DONE_MESSAGE = "done message"
__UPDATE_COMMAND = "conda env update command"
__DRIVER_VERSION = "550.54.15"
__CUDA12_ENVIRONMENT = {"id": "cuda12", "file": "conda/cuda12.yml", "min_driver_version": "525.60.13"}
__CUDA11_ENVIRONMENT = {"id": "cuda11", "file": "conda/cuda11.yml", "min_driver_version": "450.80.02"}
__NO_CUDA_ENVIRONMENT = {"id": "nocuda", "file": "conda/nocuda.yml"}
__ENVIRONMENTS = [__CUDA12_ENVIRONMENT, __CUDA11_ENVIRONMENT, __NO_CUDA_ENVIRONMENT]
__NO_ACTIVE_ENVIRONMENT_MESSAGE = (
  "No active Conda environment found. Activate the environment where Xmipp's dependencies should be installed."
)
__NO_FALLBACK_MESSAGE = "There is no Conda environment without CUDA defined for this system."
__INSTALLING_MESSAGE = (
  f"Installing environment '{__NO_CUDA_ENVIRONMENT['id']}' from "
  f"{__NO_CUDA_ENVIRONMENT['file']} into {__CONDA_PREFIX}..."
)
__CUDA_DISABLED_MESSAGE = "CUDA is disabled, selecting environment without CUDA."
__NO_DRIVER_MESSAGE = logger.yellow("Could not detect the NVIDIA driver, selecting environment without CUDA.")
__OLD_DRIVER_MESSAGE = logger.yellow(
  f"NVIDIA driver {__DRIVER_VERSION} is too old for any CUDA environment, selecting environment without CUDA."
)

def test_implements_interface_mode_executor():
  executor = ModeCondaDependenciesExecutor(__CONTEXT.copy())
  assert (
    isinstance(executor, ModeExecutor)
  ), get_assertion_message(
    "parent class",
    ModeExecutor.__name__,
    executor.__class__.__bases__[0].__name__
  )

def test_does_not_override_parent_config_values(__dummy_test_mode_executor):
  base_executor = __dummy_test_mode_executor(__CONTEXT.copy())
  executor = ModeCondaDependenciesExecutor(__CONTEXT.copy())
  base_config = (
    base_executor.logs_to_file,
    base_executor.prints_with_substitution,
    base_executor.prints_banner_on_exit,
    base_executor.sends_installation_info
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
  "keep_output,use_cuda,forced_environment_id",
  [
    pytest.param(False, True, None),
    pytest.param(True, False, "cuda12")
  ]
)
def test_stores_expected_values_when_initializing(
  keep_output,
  use_cuda,
  forced_environment_id
):
  executor = ModeCondaDependenciesExecutor({
    params.PARAM_KEEP_OUTPUT: keep_output,
    variables.CUDA: use_cuda,
    variables.CONDA_ENVIRONMENT: forced_environment_id
  })
  values = (executor.substitute, executor.use_cuda, executor.forced_environment_id)
  expected_values = (not keep_output, use_cuda, forced_environment_id)
  assert (
    values == expected_values
  ), get_assertion_message("stored values", expected_values, values)

def test_calls_get_section_message_when_running_executor(
  __mock_get_section_message,
  __mock_select_environment
):
  ModeCondaDependenciesExecutor(__CONTEXT.copy()).run()
  __mock_get_section_message.assert_called_once_with(
    "Installing dependencies in Conda environment"
  )

@pytest.mark.parametrize(
  "__mock_get_conda_executable,__mock_get_conda_prefix_path",
  [
    pytest.param(None, __CONDA_PREFIX),
    pytest.param("", __CONDA_PREFIX),
    pytest.param(__CONDA_EXECUTABLE, None),
    pytest.param(__CONDA_EXECUTABLE, ""),
    pytest.param(None, None)
  ],
  indirect=True
)
def test_returns_error_if_there_is_no_active_conda_environment_when_running_executor(
  __mock_get_conda_executable,
  __mock_get_conda_prefix_path,
  __mock_select_environment
):
  result = ModeCondaDependenciesExecutor(__CONTEXT.copy()).run()
  expected_result = (errors.CONDA_DEPENDENCIES_ERROR, __NO_ACTIVE_ENVIRONMENT_MESSAGE)
  assert (
    result == expected_result
  ), get_assertion_message("executor run result", expected_result, result)

@pytest.mark.parametrize(
  "__mock_get_conda_executable,__mock_get_conda_prefix_path",
  [
    pytest.param(None, __CONDA_PREFIX),
    pytest.param(__CONDA_EXECUTABLE, None)
  ],
  indirect=True
)
def test_does_not_call_read_environments_if_there_is_no_active_conda_environment_when_running_executor(
  __mock_get_conda_executable,
  __mock_get_conda_prefix_path,
  __mock_read_environments,
  __mock_select_environment
):
  ModeCondaDependenciesExecutor(__CONTEXT.copy()).run()
  __mock_read_environments.assert_not_called()

def test_calls_read_environments_when_running_executor(
  __mock_read_environments,
  __mock_select_environment
):
  ModeCondaDependenciesExecutor(__CONTEXT.copy()).run()
  __mock_read_environments.assert_called_once_with(paths.CONDA_ENVIRONMENTS_FILE)

@pytest.mark.parametrize(
  "__mock_read_environments",
  [
    pytest.param(FileNotFoundError("file not found")),
    pytest.param(ValueError("invalid json")),
    pytest.param(KeyError("environments")),
    pytest.param(TypeError("not iterable"))
  ],
  indirect=["__mock_read_environments"]
)
def test_returns_error_if_read_environments_fails_when_running_executor(
  __mock_read_environments,
  __mock_select_environment
):
  result = ModeCondaDependenciesExecutor(__CONTEXT.copy()).run()
  expected_result = (
    errors.CONDA_DEPENDENCIES_ERROR,
    f"Could not read Conda environments file '{paths.CONDA_ENVIRONMENTS_FILE}': {__mock_read_environments.side_effect}"
  )
  assert (
    result == expected_result
  ), get_assertion_message("executor run result", expected_result, result)

@pytest.mark.parametrize(
  "__mock_read_environments",
  [pytest.param(OSError("error"))],
  indirect=["__mock_read_environments"]
)
def test_does_not_call_select_environment_if_read_environments_fails_when_running_executor(
  __mock_read_environments,
  __mock_select_environment
):
  ModeCondaDependenciesExecutor(__CONTEXT.copy()).run()
  __mock_select_environment.assert_not_called()

def test_calls_select_environment_when_running_executor(
  __mock_read_environments,
  __mock_select_environment
):
  ModeCondaDependenciesExecutor(__CONTEXT.copy()).run()
  __mock_select_environment.assert_called_once_with(__ENVIRONMENTS)

@pytest.mark.parametrize(
  "__mock_select_environment",
  [pytest.param((None, __NO_FALLBACK_MESSAGE))],
  indirect=["__mock_select_environment"]
)
def test_returns_error_if_no_environment_is_selected_when_running_executor(
  __mock_select_environment
):
  result = ModeCondaDependenciesExecutor(__CONTEXT.copy()).run()
  expected_result = (errors.CONDA_DEPENDENCIES_ERROR, __NO_FALLBACK_MESSAGE)
  assert (
    result == expected_result
  ), get_assertion_message("executor run result", expected_result, result)

@pytest.mark.parametrize(
  "__mock_select_environment",
  [pytest.param((None, __NO_FALLBACK_MESSAGE))],
  indirect=["__mock_select_environment"]
)
def test_does_not_call_run_shell_command_in_streaming_if_no_environment_is_selected_when_running_executor(
  __mock_select_environment,
  __mock_run_shell_command_in_streaming
):
  ModeCondaDependenciesExecutor(__CONTEXT.copy()).run()
  __mock_run_shell_command_in_streaming.assert_not_called()

def test_calls_get_environment_update_command_when_running_executor(
  __mock_get_environment_update_command,
  __mock_select_environment
):
  ModeCondaDependenciesExecutor(__CONTEXT.copy()).run()
  __mock_get_environment_update_command.assert_called_once_with(
    __CONDA_EXECUTABLE,
    __CONDA_PREFIX,
    __NO_CUDA_ENVIRONMENT["file"]
  )

@pytest.mark.parametrize(
  "keep_output", [pytest.param(False), pytest.param(True)]
)
def test_calls_run_shell_command_in_streaming_when_running_executor(
  keep_output,
  __mock_run_shell_command_in_streaming,
  __mock_select_environment
):
  ModeCondaDependenciesExecutor(
    {**__CONTEXT, params.PARAM_KEEP_OUTPUT: keep_output}
  ).run()
  __mock_run_shell_command_in_streaming.assert_called_once_with(
    __UPDATE_COMMAND,
    show_output=True,
    substitute=not keep_output
  )

@pytest.mark.parametrize(
  "__mock_run_shell_command_in_streaming,expected_result",
  [
    pytest.param(0, (0, "")),
    pytest.param(1, (errors.CONDA_DEPENDENCIES_ERROR, "")),
    pytest.param(2, (errors.CONDA_DEPENDENCIES_ERROR, ""))
  ],
  indirect=["__mock_run_shell_command_in_streaming"]
)
def test_returns_expected_result_when_running_executor(
  __mock_run_shell_command_in_streaming,
  expected_result,
  __mock_select_environment
):
  result = ModeCondaDependenciesExecutor(__CONTEXT.copy()).run()
  assert (
    result == expected_result
  ), get_assertion_message("executor run result", expected_result, result)

@pytest.mark.parametrize(
  "__mock_run_shell_command_in_streaming,expected_calls",
  [
    pytest.param(
      0,
      [
        call(__SECTION_MESSAGE),
        call(__INSTALLING_MESSAGE),
        call(__DONE_MESSAGE, substitute=True)
      ]
    ),
    pytest.param(
      1,
      [
        call(__SECTION_MESSAGE),
        call(__INSTALLING_MESSAGE)
      ]
    )
  ],
  indirect=["__mock_run_shell_command_in_streaming"]
)
def test_calls_logger_with_expected_messages_when_running_executor(
  __mock_run_shell_command_in_streaming,
  expected_calls,
  __mock_logger,
  __mock_select_environment
):
  ModeCondaDependenciesExecutor(__CONTEXT.copy()).run()
  assert (
    __mock_logger.mock_calls == expected_calls
  ), get_assertion_message("logger calls", expected_calls, __mock_logger.mock_calls)

@pytest.mark.parametrize(
  "forced_environment_id", [pytest.param(None), pytest.param("cuda12")]
)
def test_calls_get_fallback_environment_if_cuda_is_disabled_when_selecting_environment(
  forced_environment_id,
  __mock_get_fallback_environment
):
  ModeCondaDependenciesExecutor({
    **__CONTEXT,
    variables.CUDA: False,
    variables.CONDA_ENVIRONMENT: forced_environment_id
  })._select_environment(__ENVIRONMENTS)
  __mock_get_fallback_environment.assert_called_once_with(__ENVIRONMENTS)

def test_does_not_call_get_driver_version_if_cuda_is_disabled_when_selecting_environment(
  __mock_get_driver_version
):
  ModeCondaDependenciesExecutor(
    {**__CONTEXT, variables.CUDA: False}
  )._select_environment(__ENVIRONMENTS)
  __mock_get_driver_version.assert_not_called()

def test_calls_logger_if_cuda_is_disabled_when_selecting_environment(__mock_logger):
  ModeCondaDependenciesExecutor(
    {**__CONTEXT, variables.CUDA: False}
  )._select_environment(__ENVIRONMENTS)
  __mock_logger.assert_called_once_with(__CUDA_DISABLED_MESSAGE)

def test_returns_fallback_environment_if_cuda_is_disabled_when_selecting_environment(
  __mock_get_fallback_environment
):
  result = ModeCondaDependenciesExecutor(
    {**__CONTEXT, variables.CUDA: False}
  )._select_environment(__ENVIRONMENTS)
  assert (
    result == __mock_get_fallback_environment()
  ), get_assertion_message("selected environment", __mock_get_fallback_environment(), result)

def test_calls_get_environment_by_id_if_environment_is_forced_when_selecting_environment(
  __mock_get_environment_by_id
):
  ModeCondaDependenciesExecutor(
    {**__CONTEXT, variables.CONDA_ENVIRONMENT: "cuda11"}
  )._select_environment(__ENVIRONMENTS)
  __mock_get_environment_by_id.assert_called_once_with(__ENVIRONMENTS, "cuda11")

def test_does_not_call_get_driver_version_if_environment_is_forced_when_selecting_environment(
  __mock_get_environment_by_id,
  __mock_get_driver_version
):
  ModeCondaDependenciesExecutor(
    {**__CONTEXT, variables.CONDA_ENVIRONMENT: "cuda11"}
  )._select_environment(__ENVIRONMENTS)
  __mock_get_driver_version.assert_not_called()

def test_returns_environment_by_id_if_environment_is_forced_when_selecting_environment(
  __mock_get_environment_by_id
):
  result = ModeCondaDependenciesExecutor(
    {**__CONTEXT, variables.CONDA_ENVIRONMENT: "cuda11"}
  )._select_environment(__ENVIRONMENTS)
  assert (
    result == __mock_get_environment_by_id()
  ), get_assertion_message("selected environment", __mock_get_environment_by_id(), result)

def test_calls_get_driver_version_if_cuda_is_enabled_when_selecting_environment(
  __mock_get_driver_version
):
  ModeCondaDependenciesExecutor(__CONTEXT.copy())._select_environment(__ENVIRONMENTS)
  __mock_get_driver_version.assert_called_once_with()

@pytest.mark.parametrize(
  "__mock_get_driver_version", [pytest.param(None), pytest.param("")],
  indirect=["__mock_get_driver_version"]
)
def test_calls_logger_with_warning_if_driver_is_not_detected_when_selecting_environment(
  __mock_get_driver_version,
  __mock_logger
):
  ModeCondaDependenciesExecutor(__CONTEXT.copy())._select_environment(__ENVIRONMENTS)
  __mock_logger.assert_called_once_with(__NO_DRIVER_MESSAGE)

@pytest.mark.parametrize(
  "__mock_get_driver_version", [pytest.param(None)],
  indirect=["__mock_get_driver_version"]
)
def test_returns_fallback_environment_if_driver_is_not_detected_when_selecting_environment(
  __mock_get_driver_version,
  __mock_get_fallback_environment,
  __mock_is_driver_compatible
):
  result = ModeCondaDependenciesExecutor(__CONTEXT.copy())._select_environment(__ENVIRONMENTS)
  __mock_is_driver_compatible.assert_not_called()
  assert (
    result == __mock_get_fallback_environment()
  ), get_assertion_message("selected environment", __mock_get_fallback_environment(), result)

@pytest.mark.parametrize(
  "__mock_is_driver_compatible,expected_calls",
  [
    pytest.param(
      [True],
      [call(__DRIVER_VERSION, __CUDA12_ENVIRONMENT["min_driver_version"])]
    ),
    pytest.param(
      [False, True],
      [
        call(__DRIVER_VERSION, __CUDA12_ENVIRONMENT["min_driver_version"]),
        call(__DRIVER_VERSION, __CUDA11_ENVIRONMENT["min_driver_version"])
      ]
    )
  ],
  indirect=["__mock_is_driver_compatible"]
)
def test_calls_is_driver_compatible_until_compatible_environment_is_found_when_selecting_environment(
  __mock_is_driver_compatible,
  expected_calls
):
  ModeCondaDependenciesExecutor(__CONTEXT.copy())._select_environment(__ENVIRONMENTS)
  assert (
    __mock_is_driver_compatible.mock_calls == expected_calls
  ), get_assertion_message("is driver compatible calls", expected_calls, __mock_is_driver_compatible.mock_calls)

def test_does_not_call_is_driver_compatible_for_environments_without_min_driver_version_when_selecting_environment(
  __mock_is_driver_compatible
):
  environments = [
    __NO_CUDA_ENVIRONMENT,
    {**__CUDA12_ENVIRONMENT, "min_driver_version": ""},
    __CUDA11_ENVIRONMENT
  ]
  ModeCondaDependenciesExecutor(__CONTEXT.copy())._select_environment(environments)
  __mock_is_driver_compatible.assert_called_once_with(
    __DRIVER_VERSION, __CUDA11_ENVIRONMENT["min_driver_version"]
  )

@pytest.mark.parametrize(
  "__mock_is_driver_compatible,expected_environment",
  [
    pytest.param([True], __CUDA12_ENVIRONMENT),
    pytest.param([False, True], __CUDA11_ENVIRONMENT)
  ],
  indirect=["__mock_is_driver_compatible"]
)
def test_returns_first_compatible_environment_if_driver_supports_it_when_selecting_environment(
  __mock_is_driver_compatible,
  expected_environment,
  __mock_get_fallback_environment
):
  result = ModeCondaDependenciesExecutor(__CONTEXT.copy())._select_environment(__ENVIRONMENTS)
  expected_result = (expected_environment, "")
  __mock_get_fallback_environment.assert_not_called()
  assert (
    result == expected_result
  ), get_assertion_message("selected environment", expected_result, result)

@pytest.mark.parametrize(
  "__mock_is_driver_compatible",
  [pytest.param([False, True])],
  indirect=["__mock_is_driver_compatible"]
)
def test_calls_logger_if_driver_supports_environment_when_selecting_environment(
  __mock_is_driver_compatible,
  __mock_logger
):
  ModeCondaDependenciesExecutor(__CONTEXT.copy())._select_environment(__ENVIRONMENTS)
  __mock_logger.assert_called_once_with(
    f"NVIDIA driver {__DRIVER_VERSION} supports environment '{__CUDA11_ENVIRONMENT['id']}'."
  )

@pytest.mark.parametrize(
  "__mock_is_driver_compatible",
  [pytest.param([False, False])],
  indirect=["__mock_is_driver_compatible"]
)
def test_calls_logger_with_warning_if_driver_is_too_old_when_selecting_environment(
  __mock_is_driver_compatible,
  __mock_logger
):
  ModeCondaDependenciesExecutor(__CONTEXT.copy())._select_environment(__ENVIRONMENTS)
  __mock_logger.assert_called_once_with(__OLD_DRIVER_MESSAGE)

@pytest.mark.parametrize(
  "__mock_is_driver_compatible",
  [pytest.param([False, False])],
  indirect=["__mock_is_driver_compatible"]
)
def test_returns_fallback_environment_if_driver_is_too_old_when_selecting_environment(
  __mock_is_driver_compatible,
  __mock_get_fallback_environment
):
  result = ModeCondaDependenciesExecutor(__CONTEXT.copy())._select_environment(__ENVIRONMENTS)
  __mock_get_fallback_environment.assert_called_once_with(__ENVIRONMENTS)
  assert (
    result == __mock_get_fallback_environment()
  ), get_assertion_message("selected environment", __mock_get_fallback_environment(), result)

@pytest.mark.parametrize(
  "environments",
  [
    pytest.param([]),
    pytest.param(__ENVIRONMENTS),
    pytest.param([{"id": "cuda12", "file": "cuda12.yml", "min_driver_version": "525", "extra": "x"}])
  ]
)
def test_returns_expected_environments_when_reading_environments(environments, tmp_path):
  environments_file = __write_environments_file(tmp_path, {"environments": environments})
  read_environments = mode_conda_dependencies_executor._read_environments(environments_file)
  assert (
    read_environments == environments
  ), get_assertion_message("environments", environments, read_environments)

@pytest.mark.parametrize(
  "environments",
  [
    pytest.param([{"file": "env.yml"}]),
    pytest.param([{"id": "env"}]),
    pytest.param([__NO_CUDA_ENVIRONMENT, {"id": "env", "min_driver_version": "525"}]),
    pytest.param(["env"])
  ]
)
def test_raises_value_error_if_environment_misses_required_keys_when_reading_environments(
  environments,
  tmp_path
):
  environments_file = __write_environments_file(tmp_path, {"environments": environments})
  with pytest.raises(ValueError, match="every environment must define 'id' and 'file'"):
    mode_conda_dependencies_executor._read_environments(environments_file)

@pytest.mark.parametrize(
  "min_driver_version",
  [pytest.param(525), pytest.param("525.x"), pytest.param("")]
)
def test_raises_value_error_if_min_driver_version_is_invalid_when_reading_environments(
  min_driver_version,
  tmp_path
):
  environments_file = __write_environments_file(
    tmp_path,
    {"environments": [{"id": "env", "file": "env.yml", "min_driver_version": min_driver_version}]}
  )
  with pytest.raises(ValueError, match="invalid min_driver_version"):
    mode_conda_dependencies_executor._read_environments(environments_file)

@pytest.mark.parametrize(
  "file_content,expected_error",
  [
    pytest.param("not json", ValueError),
    pytest.param(json.dumps({"envs": []}), KeyError),
    pytest.param(json.dumps({"environments": 5}), TypeError),
    pytest.param(json.dumps(["environments"]), TypeError)
  ]
)
def test_raises_expected_error_if_file_is_invalid_when_reading_environments(
  file_content,
  expected_error,
  tmp_path
):
  environments_file = tmp_path / "environments.json"
  environments_file.write_text(file_content, encoding="utf-8")
  with pytest.raises(expected_error):
    mode_conda_dependencies_executor._read_environments(str(environments_file))

def test_raises_os_error_if_file_does_not_exist_when_reading_environments(tmp_path):
  with pytest.raises(OSError):
    mode_conda_dependencies_executor._read_environments(str(tmp_path / "non_existing.json"))

@pytest.mark.parametrize(
  "environment_id,expected_environment",
  [
    pytest.param("cuda12", __CUDA12_ENVIRONMENT),
    pytest.param("nocuda", __NO_CUDA_ENVIRONMENT)
  ]
)
def test_returns_expected_environment_if_it_exists_when_getting_environment_by_id(
  environment_id,
  expected_environment
):
  result = mode_conda_dependencies_executor._get_environment_by_id(__ENVIRONMENTS, environment_id)
  expected_result = (expected_environment, "")
  assert (
    result == expected_result
  ), get_assertion_message("environment by id", expected_result, result)

def test_calls_logger_if_environment_exists_when_getting_environment_by_id(__mock_logger):
  mode_conda_dependencies_executor._get_environment_by_id(__ENVIRONMENTS, "cuda11")
  __mock_logger.assert_called_once_with(
    f"Selecting environment 'cuda11' set in {variables.CONDA_ENVIRONMENT}."
  )

def test_returns_error_message_if_environment_does_not_exist_when_getting_environment_by_id():
  result = mode_conda_dependencies_executor._get_environment_by_id(__ENVIRONMENTS, "cuda10")
  expected_result = (
    None,
    f"Conda environment 'cuda10' set in {variables.CONDA_ENVIRONMENT} does not exist. "
    "Available environments: cuda12, cuda11, nocuda."
  )
  assert (
    result == expected_result
  ), get_assertion_message("environment by id", expected_result, result)

def test_does_not_call_logger_if_environment_does_not_exist_when_getting_environment_by_id(
  __mock_logger
):
  mode_conda_dependencies_executor._get_environment_by_id(__ENVIRONMENTS, "cuda10")
  __mock_logger.assert_not_called()

@pytest.mark.parametrize(
  "environments,expected_environment",
  [
    pytest.param(__ENVIRONMENTS, __NO_CUDA_ENVIRONMENT),
    pytest.param(
      [__CUDA12_ENVIRONMENT, {**__NO_CUDA_ENVIRONMENT, "min_driver_version": ""}, __NO_CUDA_ENVIRONMENT],
      {**__NO_CUDA_ENVIRONMENT, "min_driver_version": ""}
    ),
    pytest.param(
      [{**__NO_CUDA_ENVIRONMENT, "min_driver_version": None}],
      {**__NO_CUDA_ENVIRONMENT, "min_driver_version": None}
    )
  ]
)
def test_returns_first_environment_without_min_driver_version_when_getting_fallback_environment(
  environments,
  expected_environment
):
  result = mode_conda_dependencies_executor._get_fallback_environment(environments)
  expected_result = (expected_environment, "")
  assert (
    result == expected_result
  ), get_assertion_message("fallback environment", expected_result, result)

@pytest.mark.parametrize(
  "environments",
  [
    pytest.param([]),
    pytest.param([__CUDA12_ENVIRONMENT, __CUDA11_ENVIRONMENT])
  ]
)
def test_returns_error_message_if_there_is_no_fallback_when_getting_fallback_environment(
  environments
):
  result = mode_conda_dependencies_executor._get_fallback_environment(environments)
  expected_result = (None, __NO_FALLBACK_MESSAGE)
  assert (
    result == expected_result
  ), get_assertion_message("fallback environment", expected_result, result)

def __write_environments_file(directory, content) -> str:
  environments_file = directory / "environments.json"
  environments_file.write_text(json.dumps(content), encoding="utf-8")
  return str(environments_file)

@pytest.fixture
def __dummy_test_mode_executor():
  class TestExecutor(ModeExecutor):
    def run(self):
      return 0, ""
  TestExecutor({}).run() # For coverage
  return TestExecutor

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

@pytest.fixture(autouse=True)
def __mock_get_done_message():
  with patch(
    "xmipp3_installer.application.logger.predefined_messages.get_done_message"
  ) as mock_method:
    mock_method.return_value = __DONE_MESSAGE
    yield mock_method

@pytest.fixture(autouse=True)
def __mock_get_conda_executable(request):
  with patch(
    "xmipp3_installer.installer.handlers.conda_handler.get_conda_executable"
  ) as mock_method:
    mock_method.return_value = getattr(request, 'param', __CONDA_EXECUTABLE)
    yield mock_method

@pytest.fixture(autouse=True)
def __mock_get_conda_prefix_path(request):
  with patch(
    "xmipp3_installer.installer.handlers.conda_handler.get_conda_prefix_path"
  ) as mock_method:
    mock_method.return_value = getattr(request, 'param', __CONDA_PREFIX)
    yield mock_method

@pytest.fixture(autouse=True)
def __mock_get_environment_update_command():
  with patch(
    "xmipp3_installer.installer.handlers.conda_handler.get_environment_update_command"
  ) as mock_method:
    mock_method.return_value = __UPDATE_COMMAND
    yield mock_method

@pytest.fixture(autouse=True)
def __mock_run_shell_command_in_streaming(request):
  with patch(
    "xmipp3_installer.installer.handlers.shell_handler.run_shell_command_in_streaming"
  ) as mock_method:
    mock_method.return_value = getattr(request, 'param', 0)
    yield mock_method

@pytest.fixture
def __mock_read_environments(request):
  with patch(
    "xmipp3_installer.installer.modes.mode_conda_dependencies_executor._read_environments"
  ) as mock_method:
    param = getattr(request, 'param', __ENVIRONMENTS)
    if isinstance(param, Exception):
      mock_method.side_effect = param
    else:
      mock_method.return_value = param
    yield mock_method

@pytest.fixture
def __mock_select_environment(request, __mock_read_environments):
  with patch(
    "xmipp3_installer.installer.modes.mode_conda_dependencies_executor.ModeCondaDependenciesExecutor._select_environment"
  ) as mock_method:
    mock_method.return_value = getattr(request, 'param', (__NO_CUDA_ENVIRONMENT, ""))
    yield mock_method

@pytest.fixture
def __mock_get_environment_by_id():
  with patch(
    "xmipp3_installer.installer.modes.mode_conda_dependencies_executor._get_environment_by_id"
  ) as mock_method:
    mock_method.return_value = (__CUDA11_ENVIRONMENT, "")
    yield mock_method

@pytest.fixture
def __mock_get_fallback_environment():
  with patch(
    "xmipp3_installer.installer.modes.mode_conda_dependencies_executor._get_fallback_environment"
  ) as mock_method:
    mock_method.return_value = (__NO_CUDA_ENVIRONMENT, "")
    yield mock_method

@pytest.fixture(autouse=True)
def __mock_get_driver_version(request):
  with patch(
    "xmipp3_installer.installer.handlers.nvidia_handler.get_driver_version"
  ) as mock_method:
    mock_method.return_value = getattr(request, 'param', __DRIVER_VERSION)
    yield mock_method

@pytest.fixture(autouse=True)
def __mock_is_driver_compatible(request):
  with patch(
    "xmipp3_installer.installer.handlers.nvidia_handler.is_driver_compatible"
  ) as mock_method:
    mock_method.side_effect = getattr(request, 'param', [True])
    yield mock_method
