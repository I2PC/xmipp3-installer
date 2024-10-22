from .. import terminal_sizes
from . import NOTE_MESSAGE

HELP_MESSAGE = {
  terminal_sizes.LARGE_TERMINAL_WIDTH: f"""Generates a config file template with default values.

{NOTE_MESSAGE}Usage: xmipp config [options]
    ---------------------------------------------
    # Options #

    -o, --overwrite                                If set, current config file will be overwritten with a new one.

Example: ./xmipp config --overwrite
""",
  terminal_sizes.SHORT_TERMINAL_WIDTH: f"""Generates a config file template with default values.

{NOTE_MESSAGE}Usage: xmipp config [options]
    ---------------------------------------------
    # Options #

    -o, --overwrite                                If set, current config
                                                   file will be overwritten
                                                   with a new one.

Example: ./xmipp config --overwrite
"""
}
