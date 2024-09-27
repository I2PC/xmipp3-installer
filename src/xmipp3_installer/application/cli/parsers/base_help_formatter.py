"""### Defines a base help formatter with extened functions to be used by the custom formatters."""

import argparse
import shutil
from typing import List, Tuple

from xmipp3_installer.application.cli import arguments
from xmipp3_installer.application.cli.parsers import format

class BaseHelpFormatter(argparse.HelpFormatter):
	"""
	### Extendes the available functions of the generic help formatter.
	"""
	__SECTION_N_DASH = 45
	__SECTION_SPACE_MODE_HELP = 2
	__SECTION_HELP_START = format.TAB_SIZE + __SECTION_N_DASH + __SECTION_SPACE_MODE_HELP
	__LINE_SIZE_LOWER_LIMIT = int(__SECTION_HELP_START * 1.5)

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

	def get_help_separator(self) -> str:
		"""
		### Returns the line that separates sections inside the help message.

		### Returns:
		- (str): Line that separates sections inside the help message.
		"""
		dashes = ['-' for _ in range(self.__SECTION_N_DASH)]
		return format.get_formatting_tabs(f"\t{''.join(dashes)}\n")

	def text_with_limits(self, previous_text: str, text: str) -> str:
		"""
		### Returns the given text, formatted so that it does not exceed the character limit by line for the param help section.

		### Params:
		- previous_text (str): Text inserted before the one to be returned.
		- text (str): The text to be formatted.

		### Returns:
		- (str): Formatted text.
		"""
		previous_length = len(format.get_formatting_tabs(previous_text))

		# Check if such length exceeds the space reserved for modes and params
		if previous_length >= self.__SECTION_HELP_START:
			# If so, it means that section space for modes and params 
			# is too low and should be set to a higher number, but for now we need to print anyways, 
			# so we reduce space from the one reserved for mode help
			remaining_space = self.__getLineSize() - previous_length

			# Add minimum fill in space possible
			fill_in_space = ' '
		else:
			# If such section is within the expected size range, calculate remaining size
			# based on the expected help section beginning
			remaining_space = self.__getLineSize() - self.__SECTION_HELP_START

			# Add fill in space
			fill_in_space = ''.join([' ' for _ in range(self.__SECTION_HELP_START - previous_length)])
		
		# Format string so it does not exceed size limit
		formatted_help = self.__multi_line_help_text(
			text,
			remaining_space,
			''.join([' ' for _ in range(self.__SECTION_HELP_START)])
		)

		return previous_text + fill_in_space + formatted_help + '\n'

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

	def __getLineSize(self) -> int:
		"""
		### Returns the maximum size for a line.

		### Returns:
		- (int): Maximum line size.
		"""
		size = shutil.get_terminal_size().columns
		return self.__LINE_SIZE_LOWER_LIMIT if size < self.__LINE_SIZE_LOWER_LIMIT else size

	def __multi_line_help_text(self, text: str, size_limit: int, left_fill: str) -> str:
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
				line, text_words = self.__fit_words_in_line(text_words, size_limit)

				# Add line to list
				if line:
					# If it's not the first line, add the left fill
					line = left_fill + line if lines else line
					lines.append(line)

			# Join lines into a single string
			formatted_text = '\n'.join(lines)
		
		# Return resulting text
		return formatted_text

	def __fit_words_in_line(self, words: List[str], size_limit: int) -> Tuple[str, List[str]]:
		"""
		### Returns a tuple containig a line with the words from the given list that could fit given the size limit, and the list with the remaining words.

		### Params:
		- words (list[str]): List of words to try to fit into a line.
		- size_limit (int): Size limit for the text.

		### Returns:
		- (str): Line with the words that were able to fit in it.
		- (list[str]): List containing the words that could not fit in the line.
		"""
		line = ''
		remaining_words = words
		for word in words:
			if self.__word_fits_in_line(line, word, size_limit):
				line, remaining_words = self.__add_word_to_line(line, word, remaining_words)
			else:
				break
		return line, remaining_words
				
	def __word_fits_in_line(self, line: str, word: str, size_limit: int) -> bool:
		"""
		### Checks if a word can fit in the current line without exceeding the size limit.

		### Params:
		- line (str): The current line of text.
		- word (str): The word to check.
		- size_limit (int): The maximum allowed size for the line.

		### Returns:
		- (bool): True if the word fits in the line, False otherwise.
		"""
		if line:
			return len(line + ' ' + word) <= size_limit
		return len(word) < size_limit

	def __add_word_to_line(self, line: str, word: str, remaining_words: list[str]) -> Tuple[str, list[str]]:
		"""
		### Adds a word to the current line and updates the list of remaining words.

		### Params:
		- line (str): The current line of text.
		- word (str): The word to add to the line.
		- remaining_words (list[str]): The list of words yet to be added to the line.

		### Returns:
		- (str): The updated line with the new word added.
		- (list[str]): The updated list of remaining words.
		"""
		if line:
			line += ' ' + word
		else:
			line = word
		return line, remaining_words[1:]
