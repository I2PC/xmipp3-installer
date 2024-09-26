"""### Defines a base help formatter with extened functions to be used by the custom formatters."""

import argparse
from typing import List

from xmipp3_installer.application.cli import arguments

class BaseHelpFormatter(argparse.HelpFormatter):
	"""
	### Extendes the available functions of the generic help formatter.
	"""
	def get_mode_help(self, mode: str, general: bool=True) -> str:
		"""
		### Returns the help message of a given mode.

		### Params:
		- mode (str): Mode to get help text for.
		- general (bool). Optional. If True, only the general help message is displayed.

		### Returns:
		- (str): Help of the mode (empty if mode not found).
		"""
		for group in list(arguments.MODES.keys()):
			if mode in list(arguments.MODES[group].keys()):
				messages = arguments.MODES[group][mode]
				return self.__get_message_from_list(messages, general)
		return ''
	
	def get_param_first_name(self, param_key: str) -> str:
		"""
		### Returns the first name of the given param key. Short name has priority over long name.

		### Params:
		- param_key (str): Key to identify the param.

		### Returns:
		- (str): Formatted text.
		"""
		param = arguments.PARAMS[param_key]
		return param.get(arguments.SHORT_VERSION, param.get(arguments.LONG_VERSION, ''))

	def __get_message_from_list(self, messages: List[str], only_general: bool) -> str:
		"""
		### Return the appropiate message given a list of them and a condition.

		#### Params:
		- messages (list[str]): List of messages.
		- only_general (bool): If True, only the general (first) message is returned.

		#### Returns:
		- (str): Expected messages in a string.
		"""
		return messages[0] if only_general else '\n'.join(messages)
