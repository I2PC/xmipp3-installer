"""### Contains a class that extends the capabilities of standard argparser."""

import argparse, shutil
from typing import List, Tuple

from .constants import (MODES, MODE_ARGS, TAB_SIZE, MODE_EXAMPLES,
	MODE_ALL, PARAMS, SHORT_VERSION, LONG_VERSION, DESCRIPTION)
from xmipp3_installer.application.logger.logger import logger

# File specific constants
__SECTION_N_DASH = 45
__SECTION_SPACE_MODE_HELP = 2
__SECTION_HELP_START = TAB_SIZE + __SECTION_N_DASH + __SECTION_SPACE_MODE_HELP
__LINE_SIZE_LOWER_LIMIT = int(__SECTION_HELP_START * 1.5)

####################### AUX FUNCTIONS #######################
def __get_line_size() -> int:
	"""
	### This function returns the maximum size for a line.

	### Returns:
	- (int): Maximum line size.
	"""
	size = shutil.get_terminal_size().columns
	return __LINE_SIZE_LOWER_LIMIT if size < __LINE_SIZE_LOWER_LIMIT else size

def __fitWordsInLine(words: List[str], size_limit: int) -> Tuple[str, List[str]]:
	"""
	### This function returns a tuple containig a line with the words from the given list that could fit given the size limit, and the list with the remaining words.

	### Params:
	- words (List[str]): List of words to try to fit into a line.
	- size_limit (int): Size limit for the text.

	### Returns:
	- (str): Line with the words that were able to fit in it.
	- (List[str]): List containing the words that could not fit in the line.
	"""
	# Initializing line and creating copy of word list
	# The copy is made because original list cannot be edited mid iteration
	line = ''
	remaining_words = words

	# Check if each word fits in the line
	for word in words:
		# If the line is not empty, len includes extra space
		if line:
			if len(line + ' ' + word) > size_limit:
				return line, remaining_words
			else:
				line += ' ' + word
				remaining_words = remaining_words[1:]
		else:
			# If the first word already exceeds the size limit,
			# it means it is a huge word, but we need to print it
			# anyways and move on to the next line
			if len(word) >= size_limit:
				return word, remaining_words[1:]
			else:
				# If word fits, add to line, and remove it from word list
				line = word
				remaining_words = remaining_words[1:]
	
	# If we exited the loop, it means all words were introduced in the line
	return line, []

def __multiLineHelpText(text: str, size_limit: int, left_fill: str) -> str:
	"""
	### This function returns the given text, formatted in several lines so that it does not exceed the given character limit.

	### Params:
	- text (str): The text to be formatted.
	- size_limit (int): Size limit for the text.
	- left_fill (str): String to add at the left of each new line.

	### Returns:
	- (str): Formatted text.
	"""
	if len(text) <= size_limit:
		# If its size is within the limits, return as is
		formatted_text = text
	else:
		# If size exceeds limits, split into lines
		# We need to calculate each word size to not split the string in the
		# middle of a word
		text_words = text.split(' ')

		# Initializing list to store lines
		lines = []

		# While there are still words outside of a line, parse them into one.
		while text_words:
			# Getting new line and removing fitted words in such line
			line, text_words = __fitWordsInLine(text_words, size_limit)

			# Add line to list
			if line:
				# If it's not the first line, add the left fill
				line = left_fill + line if lines else line
				lines.append(line)

		# Join lines into a single string
		formatted_text = '\n'.join(lines)
	
	# Return resulting text
	return formatted_text

def getFormattingTabs(text: str) -> str:
	"""
	### This method returns the given text, formatted to expand tabs into a fixed tab size.

	### Params:
	- text (str): The text to be formatted.

	### Returns:
	- (str): Formatted text.
	"""
	return text.expandtabs(TAB_SIZE)

def helpSeparator() -> str:
	"""
	### This function returns the line that separates sections inside the help message.

	### Returns:
	- (str): Line that separates sections inside the help message.
	"""
	dashes = ['-' for _ in range(__SECTION_N_DASH)]
	return getFormattingTabs(f"\t{''.join(dashes)}\n")

def textWithLimits(previous_text: str, text: str) -> str:
	"""
	### This function returns the given text, formatted so that it does not exceed the character limit by line for the param help section.

	### Params:
	- previous_text (str): Text inserted before the one to be returned.
	- text (str): The text to be formatted.

	### Returns:
	- (str): Formatted text.
	"""
	# Obtain previous text length
	previous_length = len(getFormattingTabs(previous_text))

	# Check if such length exceeds the space reserved for modes and params
	if previous_length >= __SECTION_HELP_START:
		# If so, it means that section space for modes and params 
		# is too low and should be set to a higher number, but for now we need to print anyways, 
		# so we reduce space from the one reserved for mode help
		remaining_space = __get_line_size() - previous_length

		# Add minimum fill in space possible
		fill_in_space = ' '
	else:
		# If such section is within the expected size range, calculate remaining size
		# based on the expected help section beginning
		remaining_space = __get_line_size() - __SECTION_HELP_START

		# Add fill in space
		fill_in_space = ''.join([' ' for _ in range(__SECTION_HELP_START - previous_length)])
	
	# Format string so it does not exceed size limit
	formatted_help = __multiLineHelpText(text, remaining_space, ''.join([' ' for _ in range(__SECTION_HELP_START)]))

	return previous_text + fill_in_space + formatted_help + '\n'

def getParamFirstName(param_key: str) -> str:
	"""
	### This function returns the first name of the given param key. Short name has priority over long name.

	### Params:
	- param_key (str): Key to identify the param.

	### Returns:
	- (str): Formatted text.
	"""
	return PARAMS[param_key].get(SHORT_VERSION, PARAMS[param_key].get(LONG_VERSION, ''))

####################### HELP FUNCTIONS #######################
def getModeHelp(mode: str, general: bool=True) -> str:
	"""
	### This method returns the help message of a given mode.

	### Params:
	- mode (str): Mode to get help text for.
	- general (bool). Optional. If True, only the general help message is displayed.

	### Returns:
	- (str): Help of the mode (empty if mode not found).
	"""
	# Find mode group containing current mode
	for group in list(MODES.keys()):
		if mode in list(MODES[group].keys()):
			message_list = MODES[group][mode]
			if general:
				return message_list[0]
			else:
				return '\n'.join(message_list)
	
	# If it was not found, return empty string
	return ''

def getParamNames(param_key: str) -> List[str]:
	"""
	### This method returns the list of possible names a given param has.

	### Params:
	- param_key (str): Key to find the param.

	### Returns:
	- (List[str]): List of all the names of the given param.
	"""
	name_list = [PARAMS[param_key].get(SHORT_VERSION, ''), PARAMS[param_key].get(LONG_VERSION, '')]
	return [name for name in name_list if name]

####################### PARSER CLASS #######################
class ErrorHandlerArgumentParser(argparse.ArgumentParser):
	"""
	This class overrides the error function of the standard argument parser
	to display better error messages.
	"""
	####################### OVERRIDED PUBLIC FUNCTIONS #######################
	def error(self, message):
		"""
		### This method prints through stderr the error message and exits with specific return code.
		
		#### Params:
		- message (str): Error message.
		"""
		# Getting mode and usage help from text
		text_list = self.prog.split(' ')
		mode = text_list[-1]

		# If text list only contains one item, mode is generic and
		# we need to get the help text
		if len(text_list) > 1:
			text_list = ' '.join(text_list[:-1])
			extra_line_break = '\n'
		else:
			text_list = self.format_help()
			extra_line_break = ''

		# Exiting with message
		error_message = logger.red(f"{mode}: error: {message}\n")
		self.exit(1, getFormattingTabs(f"{text_list}{extra_line_break}{error_message}"))

class GeneralHelpFormatter(argparse.HelpFormatter):
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
		for section in list(MODES.keys()):
			# Adding section separator and section name
			help_message += helpSeparator() + f"\t# {section} #\n\n"

			# Adding help text for every mode in each section
			for mode in list(MODES[section].keys()):
				help_message += self.__getModeArgsAndHelpStr(f"\t{mode} ", mode)

		# Adding epilog and returning to print
		epilog = "Example 1: ./xmipp\n"
		epilog += "Example 2: ./xmipp compileAndInstall -j 4\n"
		help_message += '\n' + epilog

		# Adding note about mode specific help
		note_message = "Note: You can also view a specific help message for each mode with \"./xmipp [mode] -h\".\n"
		note_message += f"Example: ./xmipp {MODE_ALL} -h\n"
		help_message += logger.yellow(note_message)
		return getFormattingTabs(help_message)

class ModeHelpFormatter(argparse.HelpFormatter):
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
		help_message = getModeHelp(mode, general=False) + '\n\n'

		# Get mode args
		args = MODE_ARGS[mode]

		# Add extra messages deppending on if there are args
		options_str = ''
		separator = ''
		if len(args) > 0:
			arg_names = [getParamFirstName(arg_name) for arg_name in args]
			if self.__argsContainOptional(arg_names):
				help_message += logger.yellow("Note: only params starting with '-' are optional. The rest are required.\n")
			options_str = ' [options]'
			separator = helpSeparator() + '\t# Options #\n\n'
		help_message += f'Usage: xmipp {mode}{options_str}\n{separator}'

		# Adding arg info
		for arg in args:
			help_message += textWithLimits('\t' + ', '.join(getParamNames(arg)), PARAMS[arg][DESCRIPTION])

		# Adding a few examples
		examples = MODE_EXAMPLES[mode]
		for i in range(len(examples)):
			number_str = '' if len(examples) == 1 else f' {i+1}'	
			help_message += f"\nExample{number_str}: {examples[i]}"
		
		# If any test were added, add extra line break
		if len(examples) > 0:
			help_message += '\n'

		return getFormattingTabs(help_message)
	