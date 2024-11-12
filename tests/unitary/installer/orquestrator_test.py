from unittest.mock import patch, MagicMock

import pytest

from xmipp3_installer.installer import orquestrator

@pytest.mark.parametrize(
  "n_jobs", [pytest.param(0), pytest.param(1), pytest.param(5)]
)
def test_calls_pool_when_running_parallel_jobs(n_jobs, __mock_pool):
  orquestrator.run_parallel_jobs([lambda: None], [()], n_jobs=n_jobs)
  __mock_pool.assert_called_once_with(n_jobs)

def test_calls_pool_starmap_when_running_parallel_jobs(__mock_pool):
  functions = [
    lambda: None,
    lambda: 1,
    lambda arg: arg
  ]
  args = [(), (), (5,)]
  orquestrator.run_parallel_jobs(functions, args)
  __mock_pool().starmap.assert_called_once_with(
    lambda func, args: func(*args),
    zip(functions, args)
  )

@pytest.fixture(params=[[]])
def __mock_pool(request):
  mock_pool = MagicMock()
  mock_pool.starmap.side_effect = request.param
  with patch("multiprocessing.Pool", return_value=mock_pool) as mock_method:
    yield mock_method
