"""
### User Interactions Module.

This module contains functions to handle user interactions.
"""

def get_user_confirmation(confirmation_text: str, case_sensitive: bool=True) -> bool:
  """
  ### Receives confirmation from user input.

  #### Params:
  - confirmation_text (str): The text the user needs to input to confirm.
  - case_sensitive (bool): Optional. If True, the text entered has to exactly match.

  #### Returns:
  - (bool): True if the user confirmed, False otherwise.
  """
  received_input = input()
  if not case_sensitive:
    received_input = received_input.lower()
    confirmation_text = confirmation_text.lower()
  return received_input == confirmation_text