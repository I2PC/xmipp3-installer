import multiprocessing
from unittest.mock import patch, MagicMock

import pytest

from xmipp3_installer.installer import orquestrator

from ... import get_assertion_message

@pytest.mark.parametrize(
  "n_jobs", [pytest.param(0), pytest.param(1), pytest.param(5)]
)
def test_calls_pool_when_running_parallel_jobs(n_jobs, __mock_pool):
  orquestrator.run_parallel_jobs([lambda: None], [()], n_jobs=n_jobs)
  __mock_pool.assert_called_once_with(n_jobs)

def test_calls_pool_with_all_logical_cores_by_default_when_running_parallel_jobs(__mock_pool):
  orquestrator.run_parallel_jobs([lambda: None], [()])
  __mock_pool.assert_called_once_with(multiprocessing.cpu_count())

def test_calls_zip_when_running_parallel_jobs(__mock_pool, __mock_starmap, __mock_zip):
  functions = [lambda: None, lambda: 1, lambda arg: arg]
  args = [(), (), (5,)]
  orquestrator.run_parallel_jobs(functions, args)
  __mock_zip.assert_called_once_with(functions, args)

def test_calls_pool_starmap_when_running_parallel_jobs(
  __mock_starmap,
  __mock_run_lambda,
  __mock_zip
):
  orquestrator.run_parallel_jobs([], [])
  __mock_starmap.assert_called_once_with(
    __mock_run_lambda,
    __mock_zip()
  )

@pytest.mark.parametrize(
  "funcs,args,expected_results",
  [
    pytest.param([max, min], [(1, 2, 3), (1, 2, 3)], [3, 1]),
    pytest.param([], [], [])
  ]
)
def test_returns_expected_results_when_running_parallel_jobs(funcs, args, expected_results):
  results = orquestrator.run_parallel_jobs(funcs, args, n_jobs=1)
  assert (
    results == expected_results
  ), get_assertion_message("parallel execution results", expected_results, results)

@pytest.mark.parametrize(
  "func,args,expected_result",
  [
    pytest.param(max, (1, 5, 7, 2), 7),
    pytest.param(min, (1, 5, 7, 2), 1)
  ]
)
def test_returns_expected_result_when_running_lambda(func, args, expected_result):
  result = orquestrator.__run_lambda(func, args)
  assert (
    result == expected_result
  ), get_assertion_message("lambda function execution result", expected_result, result)

@pytest.fixture
def __mock_pool():
  mock_pool = MagicMock()
  with patch("multiprocessing.Pool", return_value=mock_pool) as mock_method:
    yield mock_method

@pytest.fixture
def __mock_starmap():
  with patch("multiprocessing.pool.Pool.starmap") as mock_method:
    yield mock_method

@pytest.fixture
def __mock_zip():
  with patch("builtins.zip") as mock_method:
    mock_method.return_value = MagicMock()
    yield mock_method

@pytest.fixture
def __mock_run_lambda():
  with patch("xmipp3_installer.installer.orquestrator.__run_lambda") as mock_method:
    yield mock_method