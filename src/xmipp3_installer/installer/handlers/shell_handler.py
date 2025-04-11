"""### Functions that interact with the shell."""

import os
import subprocess
import threading

from typing import Tuple

from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.application.logger import errors

def run_shell_command(
  cmd: str,
  *,
  cwd: str='./',
  show_command: bool=False,
  show_output: bool=False,
  show_error: bool=False
) -> Tuple[int, str]:
  """
  ### This function runs the given command.

  #### Params:
  - cmd (str): Command to run.
  - cwd (str): Optional. Path to run the command from. Default is current directory.
  - show_output (bool): Optional. If True, output is printed.
  - show_error (bool): Optional. If True, errors are printed.
  - show_command (bool): Optional. If True, command is printed in blue.

  #### Returns:
  - (int): Return code.
  - (str): Output of the command, regardless of if it is an error or regular output.
  """
  if show_command:
    logger(logger.blue(cmd))
  ret_code, output_str = __run_command(cmd, cwd=cwd)

  if not ret_code and show_output:
    logger(output_str)
  
  if ret_code and show_error:
    logger(logger.red(output_str))
  
  return ret_code, output_str

def run_shell_command_in_streaming(
  cmd: str,
  cwd: str='./',
  show_output: bool=False,
  show_error: bool=False,
  substitute: bool=False
) -> int:
  """
  ### Runs the given command and shows its output as it is being generated.

  #### Params:
  - cmd (str): Command to run.
  - cwd (str): Optional. Path to run the command from. Default is current directory.
  - show_output (bool): Optional. If True, output is printed.
  - show_error (bool): Optional. If True, errors are printed.
  - substitute (bool): Optional. If True, output will replace previous line.

  #### Returns:
  - (int): Return code.
  """
  logger(cmd, substitute=substitute)
  process = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
  
  thread_out = threading.Thread(
    target=logger.log_in_streaming,
    args=(process.stdout,),
    kwargs={"show_in_terminal": show_output, "substitute": substitute, "err": False}
  )
  thread_err = threading.Thread(
    target=logger.log_in_streaming,
    args=(process.stderr,),
    kwargs={"show_in_terminal": show_error, "substitute": substitute, "err": True}
  )
  thread_out.start()
  thread_err.start()

  try:
    process.wait()
    thread_out.join()
    thread_err.join()
  except KeyboardInterrupt:
    process.returncode = errors.INTERRUPTED_ERROR
  
  return process.returncode

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
  process = subprocess.Popen(cmd, cwd=cwd, env=os.environ, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
  try:
    process.wait()
  except KeyboardInterrupt:
    return errors.INTERRUPTED_ERROR, ""
  
  ret_code = process.returncode
  output, err = process.communicate()
  output_str = output.decode() if not ret_code and output else err.decode()
  output_str = output_str[:-1] if output_str.endswith('\n') else output_str
  return ret_code, output_str
