import os
import shutil
from typing import Any

def get_assertion_message(item: str, expected: Any, received: Any) -> str:
	"""
	### Returns the assertion message for a given item and values.

	#### Params:
	- item (str): Item to compare.
	- expected (any): Expected value.
	- received (any): Received value.

	#### Returns:
	- (str): Assertion message for the given item.
	"""
	return f"Received different {item} than expected.\nExpected: {expected}\nReceived: {received}"

class MockTerminalSize:
	"""### This class is used to mock the terminal width."""
	def __init__(self, columns):
		self.columns = columns
	def __iter__(self):
		return iter((self.columns, 5))

def get_file_content(file_path: str) -> str:
	"""
	### Reads the content of the given file

	#### Params:
	- file_path (str): Path to the file

	#### Returns:
	- (str): Content of the file.
	"""
	with open(file_path, "r") as config_file:
		return config_file.read()

def normalize_string_line_endings(text: str) -> str:
	"""
	### Adapts the content of a text for different OSs.

	#### Params:
	- text (str): Text to adapt.
	"""
	return text.replace('\r\n', '\n')

def normalize_file_line_endings(file_path: str):
	"""
	### Adapts the content of a file for different OSs.

	#### Params:
	- file_path (str): Path to the file.
	"""
	content = get_file_content(file_path)
	content = normalize_string_line_endings(content)
	with open(file_path, 'w') as file:
		file.write(content)

def copy_file_from_reference(source_file: str, dest_file: str):
	"""
	### Copies the input reference file into the destination file.

	#### Params:
	- source_file (str): Input reference file.
	- dest_file (str): Destination file.
	"""
	file_directory = os.path.dirname(dest_file)
	if file_directory:
		os.makedirs(file_directory, exist_ok=True)
	shutil.copyfile(source_file, dest_file)

def get_test_file(file_path: str):
	return os.path.join(
		os.path.dirname(os.path.abspath(__file__)),
		"e2e",
		"test_files",
		file_path
	)
