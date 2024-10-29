"""### To be defined where to place this"""

import multiprocessing
from typing import List, Tuple, Callable, Any, Optional

from xmipp3_installer.installer.handlers import shell_handler

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

def get_package_version(package_name: str) -> Optional[str]:
	"""
	### Retrieves the version of a package or program by executing '[package_name] --version' command.

	Params:
	- package_name (str): Name of the package or program.

	Returns:
	- (str | None): Version information of the package or None if not found or errors happened.
	"""
	ret_code, output = shell_handler.run_shell_command(f'{package_name} --version')
	return output if ret_code == 0 else None
