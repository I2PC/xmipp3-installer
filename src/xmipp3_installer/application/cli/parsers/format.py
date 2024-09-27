"""### Common formatting functions for parsers."""

TAB_SIZE = 4

def get_formatting_tabs(text: str) -> str:
	"""
	### Returns the given text, formatted to expand tabs into a fixed tab size.

	### Params:
	- text (str): The text to be formatted.

	### Returns:
	- (str): Formatted text.
	"""
	return text.expandtabs(TAB_SIZE)
