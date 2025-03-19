"""### Common formatting functions for parsers."""

from typing import List

from xmipp3_installer.application.cli.arguments import params

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

def get_param_names(param_key: str) -> List[str]:
  """
  ### Returns the list of possible names a given param has.

  #### Params:
  - param_key (str): Key to find the param.

  #### Returns:
  - (list[str]): Names of the given param.
  """
  names = [
    params.PARAMS[param_key].get(params.SHORT_VERSION, ''),
    params.PARAMS[param_key].get(params.LONG_VERSION, '')
  ]
  return [name for name in names if name]
