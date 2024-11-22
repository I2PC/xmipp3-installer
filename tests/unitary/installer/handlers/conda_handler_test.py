from unittest.mock import patch

import pytest

from xmipp3_installer.installer.handlers import conda_handler

from .... import get_assertion_message

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

@pytest.fixture
def __mock_env_get():
	with patch("os.environ.get") as mock_method:
		yield mock_method

@pytest.fixture(params=["/path/to/conda/env"])
def __mock_env(request):
	with patch.dict(
		'os.environ', {'CONDA_PREFIX': request.param}
	):
		yield request.param
