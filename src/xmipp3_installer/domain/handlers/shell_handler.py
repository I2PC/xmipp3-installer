"""### Functions that interact with the shell."""

import os

from subprocess import Popen, PIPE
from typing import Tuple

from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.application.logger import errors

def run_shell_command(
	cmd: str,
	cwd: str='./',
	show_command: bool=False,
	show_output: bool=False,
	show_error: bool=False,
	substitute: bool=False
) -> Tuple[int, str]:
	"""
	### This function runs the given command.

	#### Params:
	- cmd (str): Command to run.
	- cwd (str): Optional. Path to run the command from. Default is current directory.
	- show_output (bool): Optional. If True, output is printed.
	- show_error (bool): Optional. If True, errors are printed.
	- show_command (bool): Optional. If True, command is printed in blue.
	- substitute (bool): Optional. If True, output will replace previous line.

	#### Returns:
	- (int): Return code.
	- (str): Output of the command, regardless of if it is an error or regular output.
	"""
	if show_command:
		logger(logger.blue(cmd), substitute=substitute)
	ret_code, output_str = __run_command(cmd, cwd=cwd)

	if not ret_code and show_output:
		logger(output_str, substitute=substitute)
	
	if ret_code and show_error:
		logger.log_error(output_str, ret_code=ret_code, substitute=substitute)
	
	return ret_code, output_str

def __run_command(cmd: str, cwd: str='./') -> Tuple[int, str]:
	"""
	### Runs the given shell command.

	#### Params:
	- cmd (str): Command to run.
	- cwd (str): Optional. Path to run the command from.

	#### Returns:
	- (int): Return code of the operation.
	- (str): Return message of the operation.
	"""
	process = Popen(cmd, cwd=cwd, env=os.environ, stdout=PIPE, stderr=PIPE, shell=True)
	try:
		process.wait()
	except KeyboardInterrupt:
		return errors.INTERRUPTED_ERROR, ""
	
	ret_code = process.returncode
	output, err = process.communicate()
	output_str = output.decode() if not ret_code and output else err.decode()
	output_str = output_str[:-1] if output_str.endswith('\n') else output_str
	return ret_code, output_str
