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
