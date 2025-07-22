"""### Defines a base help formatter with extened functions to be used by the custom formatters."""

import argparse
import shutil
from typing import List, Tuple, Union

from xmipp3_installer.application.cli.arguments import modes, params
from xmipp3_installer.application.cli.parsers import format

class BaseHelpFormatter(argparse.HelpFormatter):
  """### Extendes the available functions of the generic help formatter."""

  __SECTION_N_DASH = 68
  __SECTION_SPACE_MODE_HELP = 2
  __SECTION_HELP_START = format.TAB_SIZE + __SECTION_N_DASH + __SECTION_SPACE_MODE_HELP
  __LINE_SIZE_LOWER_LIMIT = int(__SECTION_HELP_START * 1.5)

  @staticmethod
  def _get_mode_help(mode: str, general: bool=True) -> str:
    """
    ### Returns the help message of a given mode.

    ### Params:
    - mode (str): Mode to get help text for.
    - general (bool). Optional. If True, only the general help message is displayed.

    ### Returns:
    - (str): Help of the mode (empty if mode not found).
    """
    for group in modes.MODES.keys():
      if mode in modes.MODES[group].keys():
        messages = modes.MODES[group][mode]
        return BaseHelpFormatter.__get_message_from_list(messages, general)
    return ''

  @staticmethod
  def _get_param_first_name(param_key: str) -> str:
    """
    ### Returns the first name of the given param key. Short name has priority over long name.

    ### Params:
    - param_key (str): Key to identify the param.

    ### Returns:
    - (str): Formatted text.
    """
    param = params.PARAMS[param_key]
    return param.get(params.SHORT_VERSION, param.get(params.LONG_VERSION, ''))

  def _get_help_separator(self) -> str:
    """
    ### Returns the line that separates sections inside the help message.

    ### Returns:
    - (str): Line that separates sections inside the help message.
    """
    dashes = ['-' for _ in range(self.__SECTION_N_DASH)]
    return format.get_formatting_tabs(f"\t{''.join(dashes)}\n")

  def _text_with_limits(self, previous_text: str, text: str) -> str:
    """
    ### Returns the given text, formatted so that it does not exceed the character limit by line for the param help section.

    ### Params:
    - previous_text (str): Text inserted before the one to be returned.
    - text (str): The text to be formatted.

    ### Returns:
    - (str): Formatted text.
    """
    remaining_space, fill_in_space = self.__get_spaces(previous_text)
    formatted_help = BaseHelpFormatter.__multi_line_help_text(
      text,
      remaining_space,
      self.__get_start_section_fill_in_space('')
    )
    return f"{previous_text}{fill_in_space}{formatted_help}\n"

  @staticmethod
  def _has_mutually_exclusive_groups(arg_list: List[Union[str, List[str]]]) -> bool:
    """
    ### Checks if the param list provided contains mutually exclusive groups.

    ### Params:
    - arg_list (list[str | list[str]]): List of arguments, which can be strings or lists of strings.

    ### Returns:
    - (bool): True if all elements in the list are strings, False otherwise.
    """
    return any(isinstance(arg, list) for arg in arg_list)

  @staticmethod
  def __get_text_length(text: str) -> int:
    """
    ### Returns the length of a text that might contain tabs.

    #### Params:
    - text (str): Text to measure.

    #### Returns:
    - (int): Text's length.
    """
    return len(format.get_formatting_tabs(text))

  @staticmethod
  def __get_message_from_list(messages: List[str], only_general: bool) -> str:
    """
    ### Return the appropiate message given a list of them and a condition.

    #### Params:
    - messages (list[str]): List of messages.
    - only_general (bool): If True, only the general (first) message is returned.

    #### Returns:
    - (str): Expected messages in a string.
    """
    return messages[0] if only_general else '\n'.join(messages)

  def __get_line_size(self) -> int:
    """
    ### Returns the maximum size for a line.

    ### Returns:
    - (int): Maximum line size.
    """
    size = shutil.get_terminal_size().columns
    return self.__LINE_SIZE_LOWER_LIMIT if size < self.__LINE_SIZE_LOWER_LIMIT else size

  @staticmethod
  def __multi_line_help_text(text: str, size_limit: int, left_fill: str) -> str:
    """
    ### This function returns the given text, formatted in several lines so that it does not exceed the given character limit.

    ### Params:
    - text (str): The text to be formatted.
    - size_limit (int): Size limit for the text.
    - left_fill (str): String to add at the left of each new line.

    ### Returns:
    - (str): Formatted text.
    """
    return (
      text
      if len(text) <= size_limit else
      BaseHelpFormatter.__format_text_in_lines(text, size_limit, left_fill)
    )

  @staticmethod
  def __fit_words_in_line(words: List[str], size_limit: int) -> Tuple[str, List[str]]:
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
      if BaseHelpFormatter.__word_fits_in_line(line, word, size_limit):
        line, remaining_words = BaseHelpFormatter.__add_word_to_line(line, word, remaining_words)
      else:
        break
    return line, remaining_words

  @staticmethod
  def __word_fits_in_line(line: str, word: str, size_limit: int) -> bool:
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
      return len(f"{line} {word}") <= size_limit
    return len(word) <= size_limit

  @staticmethod
  def __add_word_to_line(line: str, word: str, remaining_words: List[str]) -> Tuple[str, List[str]]:
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
      line += f" {word}"
    else:
      line = word
    return line, remaining_words[1:]

  @staticmethod
  def __format_text_in_lines(text: str, size_limit: int, left_fill: str):
    """
    ### Returns the text formatted into size-limited lines.

    #### Params:
    - text (str): Text to format.
    - size_limit (int): Max number of characters allowed in a single line.
    - left_fill (str): Starting characters of each line.

    #### Returns:
    - (str): Text formatted into lines.
    """
    words = text.split(' ')
    lines = []
    while words:
      iteration_size_limit = size_limit if size_limit >= len(words[0]) else len(words[0])
      line, words = BaseHelpFormatter.__fit_words_in_line(words, iteration_size_limit)
      line = left_fill + line if lines else line
      lines.append(line)
    return '\n'.join(lines)

  def __get_spaces(self, start_section_text: str) -> Tuple[int, str]:
    if self.__is_start_section_text_exceeding_size_limit(start_section_text):
      # If text exceeds size limit, it means that section space for modes and params 
      # is too low and should be set to a higher number, but for now we need to print anyways, 
      # so we reduce space from the one reserved for mode help and add minimum fill-in space
      remaining_space = self.__get_line_size() - BaseHelpFormatter.__get_text_length(start_section_text)
      fill_in_space = ' '
    else:
      remaining_space = self.__get_line_size() - self.__SECTION_HELP_START
      fill_in_space = self.__get_start_section_fill_in_space(start_section_text)
    return remaining_space, fill_in_space

  def __get_start_section_fill_in_space(self, text: str) -> str:
    """
    ### Returns the fill-in space for the start section.

    #### Params:
    - text (str): Text inside the start section.

    #### Returns:
    - (str): The required number of spaces to generate the start section's fill-in.
    """
    return ''.join(
      [' ' for _ in range(self.__SECTION_HELP_START - BaseHelpFormatter.__get_text_length(text))]
    )
  
  def __is_start_section_text_exceeding_size_limit(self, start_section_text: str) -> bool:
    """
    ### Indicates if the given start section text exceedes allowed size limit.

    #### Params:
    - start_section_text (str): Text to measure.

    #### Returns:
    - (bool): True if the text exceedes allowed size limit.
    """
    return BaseHelpFormatter.__get_text_length(start_section_text) >= self.__SECTION_HELP_START
