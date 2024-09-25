"""### Functions that interact with the shell."""

from typing import Tuple

def run_shell_command(cmd: str, cwd: str='./', show_output: bool=False, show_error: bool=False,
					 show_command: bool=False, substitute: bool=False, log_output: bool=False) -> Tuple[int, str]:
	"""
	### This function runs the given command.

	#### Params:
	- cmd (str): Command to run.
	- cwd (str): Optional. Path to run the command from. Default is current directory.
	- show_output (bool): Optional. If True, output is printed.
	- show_error (bool): Optional. If True, errors are printed.
	- show_command (bool): Optional. If True, command is printed in blue.
	- substitute (bool): Optional. If True, output will replace previous line.
	- log_output (bool): Optional. If True, output will be stored in the log.

	#### Returns:
	- (int): Return code.
	- (str): Output of the command, regardless of if it is an error or regular output.
	"""
	# Printing command if specified
	__logToSelection(blue(cmd), sendToLog=log_output, sendToTerminal=show_command, substitute=substitute)

	# Running command
	process = Popen(cmd, cwd=cwd, env=os.environ, stdout=PIPE, stderr=PIPE, shell=True)
	try:
		process.wait()
	except KeyboardInterrupt:
		return INTERRUPTED_ERROR, ""
	
	# Defining output string
	ret_code = process.returncode
	output, err = process.communicate()
	outputStr = output.decode() if not ret_code and output else err.decode()
	outputStr = outputStr[:-1] if outputStr.endswith('\n') else outputStr

	# Printing output if specified
	if not ret_code:
		__logToSelection(f"{outputStr}", sendToLog=log_output, sendToTerminal=show_output, substitute=substitute)

	# Printing errors if specified
	if ret_code and show_error:
		if log_output:
			logger.logError(outputStr)
		else:
			print(red(outputStr))

	# Returing return code
	return ret_code, outputStr

def run_insistent_shell_command(cmd: str, cwd: str='./', show_output: bool=False, show_error: bool=False, show_command: bool=False, n_retries: int=5) -> Tuple[int, str]:
	"""
	### This function runs the given network command and retries it the number given of times until one of the succeeds or it fails for all the retries.

	#### Params:
	- cmd (str): Command to run.
	- cwd (str): Optional. Path to run the command from. Default is current directory.
	- show_output (bool): Optional. If True, output is printed.
	- show_error (bool): Optional. If True, errors are printed.
	- show_command (bool): Optional. If True, command is printed in blue.
	- n_retries (int): Optional. Maximum number of retries for the command.

	#### Returns:
	- (int): Return code.
	- (str): Output of the command, regardless of if it is an error or regular output.
	"""
	# Running command up to n_retries times (improves resistance to small network errors)
	for _ in range(n_retries):
		ret_code, output = run_shell_command(cmd, cwd=cwd)
		# Break loop if success was achieved
		if ret_code == 0:
			break
	
	# Enforce message showing deppending on value
	if show_command:
		print(blue(cmd))
	if show_output:
		print('{}\n'.format(output))
	if show_error:
		print(red(output))
	
	# Returning output and return code
	return ret_code, output
