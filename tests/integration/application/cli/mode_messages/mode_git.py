from .. import terminal_sizes

HELP_MESSAGE = {
  terminal_sizes.LARGE_TERMINAL_WIDTH: """Runs the given git action for all source repositories.

Usage: xmipp git [options]
    ---------------------------------------------
    # Options #

    command                                        Git command to run on all source repositories.

Example 1: ./xmipp git pull
Example 2: ./xmipp git checkout devel
""",
  terminal_sizes.SHORT_TERMINAL_WIDTH: """Runs the given git action for all source repositories.

Usage: xmipp git [options]
    ---------------------------------------------
    # Options #

    command                                        Git command to run on all
                                                   source repositories.

Example 1: ./xmipp git pull
Example 2: ./xmipp git checkout devel
"""
}
