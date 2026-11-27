"""### Contains functions that orquestrate other function executions."""

from __future__ import annotations

import multiprocessing
from collections.abc import Callable
from typing import Any


def run_parallel_jobs(
  funcs: list[Callable],
  func_args: list[tuple[Any, ...]],
  n_jobs: int=multiprocessing.cpu_count()
) -> list:
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
    return p.starmap(__run_lambda, zip(funcs, func_args, strict=True))

def __run_lambda(func: Callable, args: tuple[Any, ...]) -> Any:
  """
  ### Runs the given function with its args.
  
  #### Params:
  - func (callable): Function to run.
  - args (tuple(any, ...)): Arguments for the function.
  
  #### Returns:
  - (any): Return of the called function.
  """
  return func(*args)
