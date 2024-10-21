from .. import terminal_sizes
from . import NOTE_MESSAGE

HELP_MESSAGE = {
  terminal_sizes.LARGE_TERMINAL_WIDTH: f"""Returns the version information. Add '--short' to print only the version number.

{NOTE_MESSAGE}Usage: xmipp version [options]
    ---------------------------------------------
    # Options #

    --short                                        If set, only version number is shown.

Example 1: ./xmipp version
Example 2: ./xmipp version --short
""",
  terminal_sizes.SHORT_TERMINAL_WIDTH: f"""Returns the version information. Add '--short' to print only the version number.

{NOTE_MESSAGE}Usage: xmipp version [options]
    ---------------------------------------------
    # Options #

    --short                                        If set, only version
                                                   number is shown.

Example 1: ./xmipp version
Example 2: ./xmipp version --short
"""
}
