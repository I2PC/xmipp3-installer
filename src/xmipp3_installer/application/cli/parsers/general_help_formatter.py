
from xmipp3_installer.application.cli.parsers.base_help_formatter import BaseHelpFormatter
from xmipp3_installer.application.logger.logger import logger

class GeneralHelpFormatter(BaseHelpFormatter):
	"""
	This class overrides the default help formatter to display a custom help message.
	"""
	def __getModeArgsStr(self, mode: str) -> str:
		"""
		### This method returns the args text for a given mode.

		### Params:
		- mode (str): Mode to get args text for.

		### Returns:
		- (str): Args text for given mode.
		"""
		# Getting argument list for the mode  
		arg_list = MODE_ARGS[mode]

		# Formatting every element
		param_names = []
		for param in arg_list:
			param_name = getParamFirstName(param)
			if param_name:
				param_names.append(f'[{param_name}]')

		# Returning all formatted param names as a string
		return ' '.join(param_names)

	def __getModeArgsAndHelpStr(self, previous_text: str, mode: str) -> str:
		"""
		### This method returns the args and help text for a given mode.

		### Params:
		- previous_text (str): Text inserted before the one to be returned.
		- mode (str): Mode to get help text for.

		### Returns:
		- (str): Args and help text for given mode.
		"""
		# Initializing help string to format
		mode_help_str = ''

		# Find mode group containing current mode
		mode_help_str = getModeHelp(mode)

		# Return formatted text formed by the previous text, 
		# the args for the mode, and its help text
		return textWithLimits(previous_text + self.__getModeArgsStr(mode), mode_help_str)

	def format_help(self):
		"""
		### This method prints the help message of the argument parser.
		"""
		# Base message
		help_message = "Run Xmipp's installer script\n\nUsage: xmipp [options]\n"

		# Add every section
		for section in list(arguments.MODES.keys()):
			# Adding section separator and section name
			help_message += helpSeparator() + f"\t# {section} #\n\n"

			# Adding help text for every mode in each section
			for mode in list(arguments.MODES[section].keys()):
				help_message += self.__getModeArgsAndHelpStr(f"\t{mode} ", mode)

		# Adding epilog and returning to print
		epilog = "Example 1: ./xmipp\n"
		epilog += "Example 2: ./xmipp compileAndInstall -j 4\n"
		help_message += '\n' + epilog

		# Adding note about mode specific help
		note_message = "Note: You can also view a specific help message for each mode with \"./xmipp [mode] -h\".\n"
		note_message += f"Example: ./xmipp {MODE_ALL} -h\n"
		help_message += logger.yellow(note_message)
		return self.get_formatting_tabs(help_message)
