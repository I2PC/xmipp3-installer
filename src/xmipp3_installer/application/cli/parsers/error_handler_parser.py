"""### Argparser that shows the error messages formatted in a custom way."""

import argparse
from typing import List

from xmipp3_installer.application.cli.parsers import format
from xmipp3_installer.application.logger.logger import logger

class ErrorHandlerArgumentParser(argparse.ArgumentParser):
  """### Overrides the error function of the standard argument parser to display better error messages."""

  def error(self, message):
    """
    ### Prints through stderr the error message and exits with specific return code.
    
    #### Params:
    - message (str): Error message.
    """
    args = self.__get_args()
    mode = ErrorHandlerArgumentParser.__get_mode(args)

    if ErrorHandlerArgumentParser.__is_mode_generic(args):
      args = ' '.join(args[:-1])
      extra_line_break = '\n'
    else:
      args = self.format_help()
      extra_line_break = ''

    error_message = logger.red(f"{mode}: error: {message}\n")
    self.exit(
      1,
      format.get_formatting_tabs(f"{args}{extra_line_break}{error_message}")
    )
  
  def __get_args(self) -> List[str]:
    """
    ### Obtains args from stored class data.

    #### Returns:
    - (list[str]): List of arguments.
    """
    return self.prog.split(' ')
  
  @staticmethod
  def __get_mode(args: List[str]) -> str:
    """
    ### Obtains the usage mode from the received args.

    #### Params:
    - args (list[str]): List of args received by the parser.
    
    #### Returns:
    - (str): Usage mode.
    """
    return args[-1]
  
  @staticmethod
  def __is_mode_generic(args: List[str]) -> bool:
    """
    ### Returns True if the usage mode selected is the generic one.

    #### Params:
    - args (list[str]): List of received args.

    #### Returns:
    - (bool): True if the received mode is the generic one.
    """
    return len(args) > 1
