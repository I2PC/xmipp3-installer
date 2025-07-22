"""### Help formatter specific for generic usage mode."""

from xmipp3_installer.application.cli.arguments import modes
from xmipp3_installer.application.cli.parsers import format
from xmipp3_installer.application.cli.parsers.base_help_formatter import BaseHelpFormatter
from xmipp3_installer.application.logger.logger import logger

class GeneralHelpFormatter(BaseHelpFormatter):
  """### Overrides the default help formatter to display a custom help message."""

  def format_help(self):
    """### Prints the help message of the argument parser."""
    help_message = "Run Xmipp's installer script\n\nUsage: xmipp [options]\n"
    for section in modes.MODES.keys():
      help_message += self.__get_section_message(section)
    help_message += f"\n{self.__get_epilog()}"
    help_message += self.__get_note()
    return format.get_formatting_tabs(help_message)
  
  def __get_mode_arg_group_str(self, args: str) -> str:
    """
    ### This method returns the args text for a given arg group.

    ### Params:
    - args (str): Args to format into a message string.

    ### Returns:
    - (str): Args text for given mode.
    """
    param_names = []
    for param in args:
      param_name = self._get_param_first_name(param)
      if param_name:
        param_names.append(f'[{param_name}]')
    return ' '.join(param_names)

  def __get_mode_args_str(self, mode: str) -> str:
    """
    ### This method returns the args text for a given mode.

    ### Params:
    - mode (str): Mode to get args text for.

    ### Returns:
    - (str): Args text for given mode.
    """
    args = modes.MODE_ARGS[mode]
    if not self._has_mutually_exclusive_groups(args):
      return self.__get_mode_arg_group_str(args)
    
    group_strs = [
      self.__get_mode_arg_group_str(arg_group) for arg_group in args
    ]
    exclusive_group_str = " | ".join(group_strs)
    return f"({exclusive_group_str})"

  def __get_mode_args_and_help_str(self, previous_text: str, mode: str) -> str:
    """
    ### This method returns the args and help text for a given mode.

    ### Params:
    - previous_text (str): Text inserted before the one to be returned.
    - mode (str): Mode to get help text for.

    ### Returns:
    - (str): Args and help text for given mode.
    """
    return self._text_with_limits(
      previous_text + self.__get_mode_args_str(mode),
      self._get_mode_help(mode)
    )

  @staticmethod
  def __get_epilog() -> str:
    """
    ### Returns the epilogue.

    #### Returns:
    - (str): Epilogue.
    """
    epilogue = "Example 1: ./xmipp\n"
    epilogue += "Example 2: ./xmipp compileAndInstall -j 4\n"
    return epilogue
  
  @staticmethod
  def __get_note() -> str:
    """
    ### Returns the additional note message.

    #### Returns:
    - (str): Note message.
    """
    note_message = "Note: You can also view a specific help message for each mode with \"./xmipp [mode] -h\".\n"
    note_message += f"Example: ./xmipp {modes.MODE_ALL} -h\n"
    return logger.yellow(note_message)

  def __get_section_message(self, section: str) -> str:
    """
    ### Returns the given section's message.

    #### Params:
    - section (str): Section name.

    #### Return:
    - (str): Section's message.
    """
    section_message = self._get_help_separator() + f"\t# {section} #\n\n"
    for mode in modes.MODES[section].keys():
      section_message += self.__get_mode_args_and_help_str(f"\t{mode} ", mode)
    return section_message
