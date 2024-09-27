"""### Help formatter specific for non-generic usage modes."""

from typing import List

from xmipp3_installer.application.cli import arguments
from xmipp3_installer.application.cli.parsers import format
from xmipp3_installer.application.cli.parsers.base_help_formatter import BaseHelpFormatter
from xmipp3_installer.application.logger.logger import logger

class ModeHelpFormatter(BaseHelpFormatter):
	"""
	This class overrides the default help formatter to display a custom help message deppending on the mode selected.
	"""
	def __argsContainOptional(self, arg_names: List[str]) -> bool:
		"""
		### Returns True if the param name list contains at least one optional param.

		### Params:
		- arg_names (List[str]): List containing the param names.

		### Returns:
		- (bool): True if there is at least one optional param. False otherwise.
		"""
		for name in arg_names:
			if name.startswith('-'):
				return True
		return False

	def format_help(self):
		"""
		### This method prints the help message of the argument parser.
		"""
		# Getting the selected mode from the parent help message
		# Message received is the format_help of the main parser's
		# formatter, adding the mode at the end
		mode = self._prog.split(' ')[-1]

		# Initialize the help message
		help_message = self.get_mode_help(mode, general=False) + '\n\n'

		# Get mode args
		args = arguments.MODE_ARGS[mode]

		# Add extra messages deppending on if there are args
		options_str = ''
		separator = ''
		if len(args) > 0:
			arg_names = [self.get_param_first_name(arg_name) for arg_name in args]
			if self.__argsContainOptional(arg_names):
				help_message += logger.yellow("Note: only params starting with '-' are optional. The rest are required.\n")
			options_str = ' [options]'
			separator = self.get_help_separator() + '\t# Options #\n\n'
		help_message += f'Usage: xmipp {mode}{options_str}\n{separator}'

		# Adding arg info
		for arg in args:
			help_message += self.text_with_limits('\t' + ', '.join(getParamNames(arg)), arguments.PARAMS[arg][arguments.DESCRIPTION])

		# Adding a few examples
		examples = arguments.MODE_EXAMPLES[mode]
		for i in range(len(examples)):
			number_str = '' if len(examples) == 1 else f' {i+1}'	
			help_message += f"\nExample{number_str}: {examples[i]}"
		
		# If any test were added, add extra line break
		if len(examples) > 0:
			help_message += '\n'

		return format.get_formatting_tabs(help_message)
