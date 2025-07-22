"""### Help formatter specific for non-generic usage modes."""

from typing import List, Union, cast

from xmipp3_installer.application.cli import arguments
from xmipp3_installer.application.cli.arguments import modes, params
from xmipp3_installer.application.cli.parsers import format
from xmipp3_installer.application.cli.parsers.base_help_formatter import BaseHelpFormatter
from xmipp3_installer.application.logger.logger import logger

class ModeHelpFormatter(BaseHelpFormatter):
  """### Overrides the default help formatter to display a custom help message deppending on the mode selected."""

  def format_help(self):
    """### This method prints the help message of the argument parser."""
    mode = self.__get_mode()
    help_message = f"{self._get_mode_help(mode, general=False)}\n\n"
    help_message += self.__get_args_message(mode)
    help_message += self.__get_examples_message(mode)
    return format.get_formatting_tabs(help_message)

  def __get_mode(self):
    """
    ### Returns the execution mode.

    #### Returns:
    - (str): Execution mode.
    """
    # Retrieved from the parent help message
    # Message received is the format_help output of the main parser's
    # formatter, adding the mode at the end
    return self._prog.split(' ')[-1]
  
  def __get_args_message(self, mode: str) -> str:
    """
    ### Returns the help section containing all the parameters.

    #### Params:
    - mode (str): Usage mode selected.

    #### Returns:
    - (str): Help section containing all parameters.
    """
    args = modes.MODE_ARGS[mode]
    help_message = ''
    options_str = ''
    separator = ''
    
    if len(args) > 0:
      arg_names = [
        self._get_param_first_name(arg_name) for arg_name in self.__flatten_args(args)
      ]
      if self._has_mutually_exclusive_groups(args):
        help_message += logger.yellow(
          "Important: In this mode, there are mutually exclusive groups of params. "
          "You can only use from one of them at a time.\n"
          )
      if self.__args_contain_optional(arg_names):
        help_message += logger.yellow("Note: only params starting with '-' are optional. The rest are required.\n")
      options_str = ' [options]'
      separator = self._get_help_separator() + '\t# Options #\n\n'

    help_message += f'Usage: {arguments.XMIPP_PROGRAM_NAME} {mode}{options_str}\n{separator}'
    help_message += self.__get_args_info(args)
    return help_message

  @staticmethod
  def __args_contain_optional(arg_names: List[str]) -> bool:
    """
    ### Returns True if the param name list contains at least one optional param.

    ### Params:
    - arg_names (list[str]): List containing the param names.

    ### Returns:
    - (bool): True if there is at least one optional param. False otherwise.
    """
    for name in arg_names:
      if name.startswith('-'):
        return True
    return False

  def __get_args_info(self, args: List[Union[str, List[str]]]) -> str:
    """
    ### Returns the info of each param.

    #### Params:
    - args (list[str]): List of parameters.

    #### Returns:
    - (str): Info of all parameters.
    """
    if not self._has_mutually_exclusive_groups(args):
      return self.__get_args_group_info(cast(List[str], args))
    return "\t---------------\n".join([self.__get_args_group_info(cast(List[str], group)) for group in args])

  def __get_args_group_info(self, args: List[str]) -> str:
    """
    ### Returns the info of each param.

    #### Params:
    - args (list[str]): List of parameters.

    #### Returns:
    - (str): Info of all parameters.
    """
    help_message = ''
    for arg in args:
      help_message += self._text_with_limits(
        '\t' + ', '.join(format.get_param_names(arg)),
        params.PARAMS[arg][params.DESCRIPTION]
      )
    return help_message

  @staticmethod
  def __get_examples_message(mode: str) -> str:
    """
    ### Returns the message section containig usage examples.

    #### Params:
    - mode (str): Usage mode selected.

    #### Returns:
    - (str): Message section containing usage examples.
    """
    help_message = ''
    examples = modes.MODE_EXAMPLES[mode]
    for i in range(len(examples)):
      number_str = '' if len(examples) == 1 else f' {i+1}'	
      help_message += f"\nExample{number_str}: {examples[i]}"
    
    if len(examples) > 0:
      help_message += '\n'

    return help_message

  def __flatten_args(self, args: List[Union[str, List[str]]]) -> List[str]:
    """
    ### Flattens a list of arguments.

    #### Params:
    - args (list[str | list[str]]): A list of arguments, which can include nested lists representing mutually exclusive groups.

    #### Returns:
    - (list[str]): A flattened list of arguments, where nested groups are expanded into a single list.
    """
    if not self._has_mutually_exclusive_groups(args):
      return cast(List[str], args)

    return [
      arg
      for arg_group in args
      for arg in arg_group
    ]
