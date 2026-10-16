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
