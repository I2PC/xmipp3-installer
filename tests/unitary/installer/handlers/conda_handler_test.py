import os
from unittest.mock import patch

import pytest

from xmipp3_installer.installer.handlers import conda_handler

from .... import get_assertion_message

__CONDA_PREFIX = "/path/to/conda/env"
__NVCC_PATH = os.path.join(__CONDA_PREFIX, "bin", "nvcc")

def test_calls_env_get_when_getting_conda_prefix(__mock_env_get):
  conda_handler.get_conda_prefix_path()
  __mock_env_get.assert_called_once_with('CONDA_PREFIX')

@pytest.mark.parametrize(
  "__mock_env",
  [pytest.param("/conda"), pytest.param("/conda-env")],
  indirect=["__mock_env"]
)
def test_returns_expectedget_conda_prefix_path_with_env_var(__mock_env):
  conda_prefix = conda_handler.get_conda_prefix_path()
  assert (
    conda_prefix == __mock_env
  ), get_assertion_message("conda prefix", __mock_env, conda_prefix)

def test_calls_env_get_when_getting_conda_executable(__mock_env_get):
  conda_handler.get_conda_executable()
  __mock_env_get.assert_called_once_with('CONDA_EXE')

@pytest.mark.parametrize(
  "conda_executable",
  [pytest.param("/conda/bin/conda"), pytest.param("/miniforge/bin/conda")]
)
def test_returns_expected_conda_executable_with_env_var(conda_executable):
  with patch.dict('os.environ', {'CONDA_EXE': conda_executable}):
    received_executable = conda_handler.get_conda_executable()
  assert (
    received_executable == conda_executable
  ), get_assertion_message("conda executable", conda_executable, received_executable)

def test_returns_none_conda_executable_without_env_var():
  with patch.dict('os.environ', clear=True):
    conda_executable = conda_handler.get_conda_executable()
  assert (
    conda_executable is None
  ), get_assertion_message("conda executable", None, conda_executable)

def test_calls_get_conda_prefix_path_when_getting_cuda_compiler_path(
  __mock_get_conda_prefix_path,
  __mock_isfile
):
  conda_handler.get_cuda_compiler_path()
  __mock_get_conda_prefix_path.assert_called_once_with()

def test_calls_isfile_with_conda_nvcc_path_when_getting_cuda_compiler_path(
  __mock_get_conda_prefix_path,
  __mock_isfile
):
  conda_handler.get_cuda_compiler_path()
  __mock_isfile.assert_called_once_with(__NVCC_PATH)

@pytest.mark.parametrize(
  "__mock_get_conda_prefix_path",
  [pytest.param(None), pytest.param("")],
  indirect=["__mock_get_conda_prefix_path"]
)
def test_does_not_call_isfile_if_there_is_no_conda_prefix_when_getting_cuda_compiler_path(
  __mock_get_conda_prefix_path,
  __mock_isfile
):
  conda_handler.get_cuda_compiler_path()
  __mock_isfile.assert_not_called()

@pytest.mark.parametrize(
  "__mock_get_conda_prefix_path,__mock_isfile,expected_path",
  [
    pytest.param(None, True, None),
    pytest.param("", True, None),
    pytest.param(__CONDA_PREFIX, False, None),
    pytest.param(__CONDA_PREFIX, True, __NVCC_PATH)
  ],
  indirect=["__mock_get_conda_prefix_path", "__mock_isfile"]
)
def test_returns_expected_cuda_compiler_path(
  __mock_get_conda_prefix_path,
  __mock_isfile,
  expected_path
):
  cuda_compiler_path = conda_handler.get_cuda_compiler_path()
  assert (
    cuda_compiler_path == expected_path
  ), get_assertion_message("CUDA compiler path", expected_path, cuda_compiler_path)

@pytest.mark.parametrize(
  "conda_executable,conda_prefix,environment_file,expected_command",
  [
    pytest.param(
      "/conda/bin/conda", "/conda/envs/xmipp", "conda/env.yml",
      '"/conda/bin/conda" env update --prefix "/conda/envs/xmipp" --file "conda/env.yml"'
    ),
    pytest.param(
      "/my conda/bin/mamba", "/my conda/envs/x y", "conda/cuda 12.yml",
      '"/my conda/bin/mamba" env update --prefix "/my conda/envs/x y" --file "conda/cuda 12.yml"'
    )
  ]
)
def test_returns_expected_environment_update_command(
  conda_executable,
  conda_prefix,
  environment_file,
  expected_command
):
  command = conda_handler.get_environment_update_command(
    conda_executable, conda_prefix, environment_file
  )
  assert (
    command == expected_command
  ), get_assertion_message("environment update command", expected_command, command)

@pytest.mark.parametrize(
  "conda_executable,expected_command",
  [
    pytest.param(
      "/conda/bin/conda",
      "bash -c 'eval \"$(/conda/bin/conda shell.bash reactivate)\" && env -0'"
    ),
    pytest.param(
      "/my conda/bin/conda",
      "bash -c 'eval \"$('\"'\"'/my conda/bin/conda'\"'\"' shell.bash reactivate)\" && env -0'"
    )
  ]
)
def test_returns_expected_reactivation_command(conda_executable, expected_command):
  command = conda_handler._get_reactivation_command(conda_executable)
  assert (
    command == expected_command
  ), get_assertion_message("reactivation command", expected_command, command)

@pytest.mark.parametrize(
  "output,expected_environment",
  [
    pytest.param("", {}),
    pytest.param("A=1\0B=2\0", {"A": "1", "B": "2"}),
    pytest.param("A=x=y\0B=\0", {"A": "x=y", "B": ""}),
    pytest.param("A=multi\nline\0", {"A": "multi\nline"})
  ]
)
def test_returns_expected_environment_when_parsing_environment(output, expected_environment):
  environment = conda_handler._parse_environment(output)
  assert (
    environment == expected_environment
  ), get_assertion_message("environment", expected_environment, environment)

def test_calls_run_shell_command_with_reactivation_command_when_reactivating_environment(
  __mock_run_shell_command
):
  with patch.dict('os.environ', {}):
    conda_handler.reactivate_environment("/conda/bin/conda")
  __mock_run_shell_command.assert_called_once_with(
    conda_handler._get_reactivation_command("/conda/bin/conda")
  )

@pytest.mark.parametrize(
  "__mock_run_shell_command,expected_result",
  [
    pytest.param((0, "CC=gcc\0"), True),
    pytest.param((1, "CC=gcc\0"), False),
    pytest.param((0, ""), False)
  ],
  indirect=["__mock_run_shell_command"]
)
def test_returns_expected_result_when_reactivating_environment(
  __mock_run_shell_command,
  expected_result
):
  with patch.dict('os.environ', {}):
    result = conda_handler.reactivate_environment("/conda/bin/conda")
  assert (
    result == expected_result
  ), get_assertion_message("reactivation result", expected_result, result)

@pytest.mark.parametrize(
  "__mock_run_shell_command,expected_environment",
  [
    pytest.param((0, "CC=gcc\0PATH=/env/bin\0"), {"CC": "gcc", "PATH": "/env/bin"}),
    pytest.param((1, "CC=gcc\0"), {"OLD": "value"}),
    pytest.param((0, ""), {"OLD": "value"})
  ],
  indirect=["__mock_run_shell_command"]
)
def test_sets_expected_environment_when_reactivating_environment(
  __mock_run_shell_command,
  expected_environment
):
  with patch.dict('os.environ', {"OLD": "value"}, clear=True):
    conda_handler.reactivate_environment("/conda/bin/conda")
    environment = dict(os.environ)
  assert (
    environment == expected_environment
  ), get_assertion_message("environment", expected_environment, environment)

@pytest.fixture
def __mock_get_conda_prefix_path(request):
  with patch(
    "xmipp3_installer.installer.handlers.conda_handler.get_conda_prefix_path"
  ) as mock_method:
    mock_method.return_value = getattr(request, 'param', __CONDA_PREFIX)
    yield mock_method

@pytest.fixture
def __mock_isfile(request):
  with patch("os.path.isfile") as mock_method:
    mock_method.return_value = getattr(request, 'param', True)
    yield mock_method

@pytest.fixture
def __mock_env_get():
  with patch("os.environ.get") as mock_method:
    yield mock_method

@pytest.fixture
def __mock_env(request):
  with patch.dict(
    'os.environ', {'CONDA_PREFIX': getattr(request, 'param', "/path/to/conda/env")}
  ):
    yield getattr(request, 'param', "/path/to/conda/env")

@pytest.fixture
def __mock_run_shell_command(request):
  with patch(
    "xmipp3_installer.installer.handlers.shell_handler.run_shell_command"
  ) as mock_method:
    mock_method.return_value = getattr(request, 'param', (0, "CC=gcc\0"))
    yield mock_method
