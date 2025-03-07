from .. import terminal_sizes
from . import NOTE_MESSAGE

HELP_MESSAGE = {
  terminal_sizes.LARGE_TERMINAL_WIDTH: f"""Compiles and installs Xmipp based on already obtained sources.

{NOTE_MESSAGE}Usage: xmipp compileAndInstall [options]
    ---------------------------------------------
    # Options #

    -j, --jobs                                     Number of jobs. Defaults to all available.
    --keep-output                                  If set, output sent through the terminal won't substitute lines, looking more like the log.

Example 1: ./xmipp compileAndInstall
Example 2: ./xmipp compileAndInstall -j 20
""",
  terminal_sizes.SHORT_TERMINAL_WIDTH: f"""Compiles and installs Xmipp based on already obtained sources.

{NOTE_MESSAGE}Usage: xmipp compileAndInstall [options]
    ---------------------------------------------
    # Options #

    -j, --jobs                                     Number of jobs. Defaults
                                                   to all available.
    --keep-output                                  If set, output sent
                                                   through the terminal
                                                   won't substitute lines,
                                                   looking more like the
                                                   log.

Example 1: ./xmipp compileAndInstall
Example 2: ./xmipp compileAndInstall -j 20
"""
}
