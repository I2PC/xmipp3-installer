"""### Contains functions that orquestrate other function executions."""

import multiprocessing
from typing import List, Tuple, Callable, Any

def run_parallel_jobs(
  funcs: List[Callable],
  func_args: List[Tuple[Any, ...]],
  n_jobs: int=multiprocessing.cpu_count()
) -> List:
  """
  ### Runs the given command list in parallel.

  #### Params:
  - funcs (list(callable)): Functions to run.
  - func_args (list(tuple(any, ...))): Arguments for each function.
  - n_jobs (int): Optional. Number of parallel jobs.

  #### Returns:
  - (list): List containing the return of each function.
  """
  with multiprocessing.Pool(n_jobs) as p:
    results = p.starmap(__run_lambda, zip(funcs, func_args))
  return results

def __run_lambda(func: Callable, args: Tuple[Any]) -> Any:
  """
  ### Runs the given function with its args.
  
  #### Params:
  - func (callable): Function to run.
  - args (tuple(any)): Arguments for the function.
  
  #### Returns:
  - (any): Return of the called function.
  """
  return func(*args)
