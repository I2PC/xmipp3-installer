from .. import terminal_sizes
from . import NOTE_MESSAGE

HELP_MESSAGE = {
  terminal_sizes.LARGE_TERMINAL_WIDTH: f"""Configures the project with CMake.

{NOTE_MESSAGE}Usage: xmipp configBuild [options]
    ---------------------------------------------
    # Options #

    --keep-output                                  If set, output sent through the terminal won't substitute lines, looking more like the log.
""",
  terminal_sizes.SHORT_TERMINAL_WIDTH: f"""Configures the project with CMake.

{NOTE_MESSAGE}Usage: xmipp configBuild [options]
    ---------------------------------------------
    # Options #

    --keep-output                                  If set, output sent
                                                   through the terminal
                                                   won't substitute lines,
                                                   looking more like the
                                                   log.
"""
}
