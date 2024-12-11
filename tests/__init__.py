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

def normalize_line_endings(file_path: str):
	"""
	### Adapts the content of a file for different OSs.

	#### Params:
	- file_path (str): 
	"""
	content = get_file_content(file_path)
	content = content.replace('\r\n', '\n')
	with open(file_path, 'w') as file:
		file.write(content)
