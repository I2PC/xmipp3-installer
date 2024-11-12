"""### Contains functions that orquestrate other function executions."""

import multiprocessing
from typing import List, Tuple, Callable, Any

def run_parallel_jobs(funcs: List[Callable], func_args: List[Tuple[Any]], n_jobs: int=multiprocessing.cpu_count()) -> List:
	"""
	### Runs the given command list in parallel.

	#### Params:
	- funcs (list(callable)): Functions to run.
	- func_args (list(tuple(any))): Arguments for each function.
	- n_jobs (int): Optional. Number of parallel jobs.

	#### Returns:
	- (list): List containing the return of each function.
	"""
	with multiprocessing.Pool(n_jobs) as p:
		results = p.starmap(lambda func, args: func(*args), zip(funcs, func_args))
	return results
