"""### Provides a global logger."""

import math
import shutil

from xmipp3_installer.application.logger import errors
from xmipp3_installer.application.logger import urls

class Logger:
	"""
	### Logger class for keeping track of installation messages.
	"""

	__UP = "\x1B[1A\r"
	__REMOVE_LINE = '\033[K'
	__BOLD = "\033[1m"
	__BLUE = "\033[34m"
	__RED = "\033[91m"
	__GREEN = "\033[92m"
	__YELLOW = "\033[93m"
	__END_FORMAT = "\033[0m"
	__FORMATTING_CHARACTERS = [__UP, __REMOVE_LINE, __BOLD, __BLUE, __RED, __GREEN, __YELLOW, __END_FORMAT]
 
	def __init__(self, output_to_console: bool = False):
		"""
		### Constructor.
		
		#### Params:
		- ouputToConsoloe (bool): Print messages to console.
		"""
		self.__log_file = None
		self.__output_to_console = output_to_console
		self.__len_last_printed_elem = 0
		self.__allow_substitution = True
	
	def green(self, text: str) -> str:
		"""
		### This function returns the given text formatted in green color.

		#### Params:
		- text (str): Text to format.

		#### Returns:
		- (str): Text formatted in green color.
		"""
		return self.__format_text(text, self.__GREEN)

	def yellow(self, text: str) -> str:
		"""
		### This function returns the given text formatted in yellow color.

		#### Params:
		- text (str): Text to format.

		#### Returns:
		- (str): Text formatted in yellow color.
		"""
		return self.__format_text(text, self.__YELLOW)

	def red(self, text: str) -> str:
		"""
		### This function returns the given text formatted in red color.

		#### Params:
		- text (str): Text to format.

		#### Returns:
		- (str): Text formatted in red color.
		"""
		return self.__format_text(text, self.__RED)

	def blue(self, text: str) -> str:
		"""
		### This function returns the given text formatted in blue color.

		#### Params:
		- text (str): Text to format.

		#### Returns:
		- (str): Text formatted in blue color.
		"""
		return self.__format_text(text, self.__BLUE)

	def bold(self, text: str) -> str:
		"""
		### This function returns the given text formatted in bold.

		#### Params:
		- text (str): Text to format.

		#### Returns:
		- (str): Text formatted in bold.
		"""
		return self.__format_text(text, self.__BOLD)

	def start_log_file(self, log_path: str):
		"""
		### Initiates the log file.

		#### Params:
		- log_path (str): Path to the log file.
		"""
		self.__log_file = open(log_path, 'w')

	def set_console_output(self, output_to_console: bool):
		"""
		### Modifies console output behaviour.
		
		#### Params:
		- ouputToConsoloe (str): Enable printing messages to console.
		"""
		self.__output_to_console = output_to_console
 
	def set_allow_substitution(self, allow_substitution: bool):
		"""
		### Modifies console output behaviour, allowing or disallowing substitutions.
		
		#### Params:
		- allow_substitution (bool): If False, console outputs won't be substituted.
		"""
		self.__allow_substitution = allow_substitution

	def __call__(self, text: str, force_console_output: bool = False, substitute: bool = False):
		"""
		### Log a message.
		
		#### Params:
		- text (str): Message to be logged. Supports fancy formatting.
		- force_console_output (bool): Optional. If True, text is also printed through terminal.
		- substitute (bool): Optional. If True, previous line is substituted with new text. Only used when force_console_output = True.
		"""
		if self.__log_file is not None:
			print(self.__remove_non_printable(text), file=self.__log_file, flush=True)
			
		if self.__output_to_console or force_console_output:
			# Calculate number of lines to substitute if substitution was requested
			substitution_str = ''.join([f'{self.__UP}{self.__REMOVE_LINE}' for _ in range(self.__get_n_last_lines())])
			text = f"{substitution_str}{text}" if self.__allow_substitution and substitute else text
			print(text, flush=True)
			# Store length of printed string for next substitution calculation
			self.__len_last_printed_elem = len(self.__remove_non_printable(text))
	 
	def log_error(self, error_msg: str, ret_code: int=1, add_portal_link: bool=True):
		"""
		### This function prints an error message.

		#### Params:
		- error_msg (str): Error message to show.
		- ret_code (int): Optional. Return code to end the exection with.
		- add_portal_link (bool): If True, a message linking the documentation portal is shown.
		"""
		error_str = error_msg + '\n\n'
		error_str += f'Error {ret_code}: {errors.ERROR_CODES[ret_code][0]}'
		error_str += f"\n{errors.ERROR_CODES[ret_code][1]} " if errors.ERROR_CODES[ret_code][1] else ''
		if add_portal_link:
			error_str += f'\nMore details on the Xmipp documentation portal: {urls.DOCUMENTATION_URL}'

		self.__call__(self.red(error_str), force_console_output=True)

	def __remove_non_printable(self, text: str) -> str:
		"""
		### This function returns the given text without non printable characters.

		#### Params:
		- text (str): Text to remove format.

		#### Returns:
		- (str): Text without format.
		"""
		for formatting_char in self.__FORMATTING_CHARACTERS:
			text = text.replace(formatting_char, "")
		return text

	def __get_n_last_lines(self) -> int:
		"""
		### This function returns the number of lines of the terminal the last print occupied.

		#### Returns:
		- (int): Number of lines of the last print. 
		"""
		return math.ceil(self.__len_last_printed_elem / shutil.get_terminal_size().columns)
	
	def __format_text(self, text: str, format_code: str) -> str:
		"""
		### Returns the given text formatted in bold.

		#### Params:
		- text (str): Text to format.
		- format_code (str): Formatting character.

		#### Returns:
		- (str): Text formatted in bold.
		"""
		return f"{format_code}{text}{self.__END_FORMAT}"

"""
### Global logger.
"""
logger = Logger()
