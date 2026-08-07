"""### Provides a global logger."""

import shutil
from contextlib import ExitStack
from io import BufferedReader

from xmipp3_installer.application.logger import errors
from xmipp3_installer.installer import urls
from xmipp3_installer.shared.singleton import Singleton


class Logger(Singleton):
  """### Logger class for keeping track of installation messages."""

  _UP = "\x1B[1A\r"
  _REMOVE_LINE = '\033[K'
  _BOLD = "\033[1m"
  _BLUE = "\033[34m"
  _RED = "\033[91m"
  _GREEN = "\033[92m"
  _YELLOW = "\033[93m"
  _END_FORMAT = "\033[0m"
  _FORMATTING_CHARACTERS = (_UP, _REMOVE_LINE, _BOLD, _BLUE, _RED, _GREEN, _YELLOW, _END_FORMAT)
 
  def __init__(self):
    """
    ### Constructor.
    
    #### Params:
    - outputToConsole (bool): Print messages to console.
    """
    self._stack = ExitStack()
    self._log_file = None
    self._last_printed_elem = None
    self._allow_substitution = True
  
  def green(self, text: str) -> str:
    """
    ### This function returns the given text formatted in green color.

    #### Params:
    - text (str): Text to format.

    #### Returns:
    - (str): Text formatted in green color.
    """
    return self._format_text(text, self._GREEN)

  def yellow(self, text: str) -> str:
    """
    ### This function returns the given text formatted in yellow color.

    #### Params:
    - text (str): Text to format.

    #### Returns:
    - (str): Text formatted in yellow color.
    """
    return self._format_text(text, self._YELLOW)

  def red(self, text: str) -> str:
    """
    ### This function returns the given text formatted in red color.

    #### Params:
    - text (str): Text to format.

    #### Returns:
    - (str): Text formatted in red color.
    """
    return self._format_text(text, self._RED)

  def blue(self, text: str) -> str:
    """
    ### This function returns the given text formatted in blue color.

    #### Params:
    - text (str): Text to format.

    #### Returns:
    - (str): Text formatted in blue color.
    """
    return self._format_text(text, self._BLUE)

  def bold(self, text: str) -> str:
    """
    ### This function returns the given text formatted in bold.

    #### Params:
    - text (str): Text to format.

    #### Returns:
    - (str): Text formatted in bold.
    """
    return self._format_text(text, self._BOLD)

  def start_log_file(self, log_path: str):
    """
    ### Initiates the log file.

    #### Params:
    - log_path (str): Path to the log file.
    """
    if self._log_file is None:
      self._log_file = self._stack.enter_context(
        open(log_path, 'w', encoding="utf-8") # noqa: SIM115 TODO change logger with loggin lib
      )

  def close(self):
    """### Closes the log file."""
    self._stack.close()
    self._log_file = None

  def set_allow_substitution(self, allow_substitution: bool):
    """
    ### Modifies console output behaviour, allowing or disallowing substitutions.
    
    #### Params:
    - allow_substitution (bool): If False, console outputs won't be substituted.
    """
    self._allow_substitution = allow_substitution

  def __call__(self, text: str, show_in_terminal: bool=True, substitute: bool=False):
    """
    ### Log a message.
    
    #### Params:
    - text (str): Message to be logged. Supports fancy formatting.
    - show_in_terminal (bool): Optional. If True, text is also printed through terminal.
    - substitute (bool): Optional. If True, previous line is substituted with new text. Only used when show_in_terminal = True.
    """
    if self._log_file is not None:
      print(self._remove_non_printable(text), file=self._log_file, flush=True)
      
    if show_in_terminal:
      text = self._substitute_lines(text) if self._allow_substitution and substitute else text
      print(text, flush=True)
    
    # Store printed string for next substitution calculation
    self._last_printed_elem = self._remove_non_printable(text) if self._allow_substitution and substitute else None
   
  def log_error(self, error_msg: str, ret_code: int=1, add_portal_link: bool=True):
    """
    ### Prints an error message.

    #### Params:
    - error_msg (str): Error message to show.
    - ret_code (int): Optional. Return code to end the exection with.
    - add_portal_link (bool): If True, a message linking the documentation portal is shown.
    """
    error = errors.ERROR_CODES.get(ret_code, errors.ERROR_CODES[errors.UNKOW_ERROR])
    error_str = error_msg + '\n\n' if error_msg else ''
    error_str += f'Error {ret_code}: {error[0]}'
    error_str += f"\n{error[1]}" if error[1] else ''
    if add_portal_link:
      error_str += f'\nMore details on the Xmipp documentation portal: {urls.DOCUMENTATION_URL}'

    self.__call__(self.red(error_str), show_in_terminal=True)

  def log_in_streaming(self, stream: BufferedReader, show_in_terminal: bool=False, substitute: bool=False, err: bool=False):
    """
    ### Receives a process output stream and logs its lines.

    #### Params:
    - stream (BufferedReader): Function to run.
    - show_in_terminal (bool): Optional. If True, output will also be printed through terminal.
    - substitute (bool): Optional. If True, output will replace previous line. Only used when show is True.
    - err (bool): Optional. If True, the stream contains an error. Otherwise, it is regular output.
    """
    for line in iter(stream.readline, b''):
      calling_line = line.decode().replace("\n", "")
      if err:
        calling_line = self.red(calling_line)
      self.__call__(calling_line, show_in_terminal=show_in_terminal, substitute=substitute)

  def _remove_non_printable(self, text: str) -> str:
    """
    ### This function returns the given text without non printable characters.

    #### Params:
    - text (str): Text to remove format.

    #### Returns:
    - (str): Text without format.
    """
    for formatting_char in self._FORMATTING_CHARACTERS:
      text = text.replace(formatting_char, "")
    return text

  def _get_n_last_lines(self) -> int:
    """
    ### This function returns the number of lines of the terminal the last print occupied.

    #### Returns:
    - (int): Number of lines of the last print. 
    """
    if self._last_printed_elem is None:
      return 0
    
    terminal_width = shutil.get_terminal_size().columns
    # At least one line break exists, as prints end with line break
    n_line_breaks = self._last_printed_elem.count("\n") + 1
    text_lines = self._last_printed_elem.split("\n")
    for line in text_lines:
      n_line_breaks += len(line) // (terminal_width + 1) # Equal does not count, it needs to exceed
    return n_line_breaks
  
  def _format_text(self, text: str, format_code: str) -> str:
    """
    ### Returns the given text formatted in the given format code.

    #### Params:
    - text (str): Text to format.
    - format_code (str): Formatting character.

    #### Returns:
    - (str): Text formatted.
    """
    return f"{format_code}{text}{self._END_FORMAT}"

  def _substitute_lines(self, text: str) -> str:
    """
    ### Removes the appropiate lines from the terminal to show a given text.

    #### Params:
    - text (str): Text to show substituting some lines.

    #### Returns:
    - (str): Text with line substitution characters as a prefix.
    """
    substitution_chars = [f'{self._UP}{self._REMOVE_LINE}' for _ in range(self._get_n_last_lines())]
    return f"{''.join(substitution_chars)}{text}"
  
"""
### Global logger.
"""
logger = Logger()
