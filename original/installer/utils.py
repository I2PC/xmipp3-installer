# ***************************************************************************
# * Authors:		Alberto García (alberto.garcia@cnb.csic.es)
# *							Martín Salinas (martin.salinas@cnb.csic.es)
# *
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307 USA
# *
# * All comments concerning this program package may be sent to the
# * e-mail address 'scipion@cnb.csic.es'
# ***************************************************************************/

"""
Module containing useful functions used by the installation process.
"""

# General imports
import multiprocessing
from typing import List, Tuple, Callable, Any, Optional
from subprocess import Popen, PIPE
from threading import Thread
from io import BufferedReader

# Installer imports
from .constants import INTERRUPTED_ERROR

####################### RUN FUNCTIONS #######################
def runParallelJobs(funcs: List[Tuple[Callable, Tuple[Any]]], nJobs: int=multiprocessing.cpu_count()) -> List:
	"""
	### This function runs the given command list in parallel.

	#### Params:
	- funcs (list(tuple(callable, tuple(any)))): Functions to run with parameters, if there are any.

	#### Returns:
	- (list): List containing the return of each function.
	"""
	# Creating a pool of n concurrent jobs
	with multiprocessing.Pool(nJobs) as p:
		# Run each function and obtain results
		results = p.starmap(__runLambda, funcs)
	
	# Return obtained result list
	return results

def runStreamingJob(cmd: str, cwd: str='./', showOutput: bool=False, showError: bool=False, substitute: bool=False) -> int:
	"""
	### This function runs the given command and shows its output as it is being generated.

	#### Params:
	- cmd (str): Command to run.
	- cwd (str): Optional. Path to run the command from. Default is current directory.
	- showOutput (bool): Optional. If True, output is printed.
	- showError (bool): Optional. If True, errors are printed.
	- substitute (bool): Optional. If True, output will replace previous line.

	#### Returns:
	- (int): Return code.
	"""
	# Create a Popen instance and error stack
	logger(cmd)
	process = Popen(cmd, cwd=cwd, stdout=PIPE, stderr=PIPE, shell=True)
	
	# Create and start threads for handling stdout and stderr
	threadOut = Thread(target=__handleOutput, args=(process.stdout, showOutput, substitute))
	threadErr = Thread(target=__handleOutput, args=(process.stderr, showError, substitute, True))
	threadOut.start()
	threadErr.start()

	# Wait for execution, handling keyboard interruptions
	try:
		process.wait()
		threadOut.join()
		threadErr.join()
	except (KeyboardInterrupt):
		process.returncode = INTERRUPTED_ERROR
	
	return process.returncode

####################### VERSION FUNCTIONS #######################
def getPackageVersionCmd(packageName: str) -> Optional[str]:
	"""
	### Retrieves the version of a package or program by executing '[packageName] --version' command.

	Params:
	- packageName (str): Name of the package or program.

	Returns:
	- (str | None): Version information of the package or None if not found or errors happened.
	"""
	# Running command
	retCode, output = runJob(f'{packageName} --version')

	# Check result if there were no errors
	return output if retCode == 0 else None

####################### AUX FUNCTIONS (INTERNAL USE ONLY) #######################
def __runLambda(function: Callable, args: Tuple[Any]=()):
	"""
	### This function is used to run other functions (intented for use inside a worker pool, so it can be picked).

	#### Params:
	- function (callable): Function to run.
	- args (tuple(any)): Optional. Function arguments.

	#### Returns:
	- (Any): Return value/(s) of the called function.
	"""
	return function(*args)
