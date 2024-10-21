from .. import terminal_sizes
from . import NOTE_MESSAGE

HELP_MESSAGE = {
  terminal_sizes.LARGE_TERMINAL_WIDTH: f"""Default param. Runs config, configBuild, and compileAndInstall.

{NOTE_MESSAGE}Usage: xmipp all [options]
    ---------------------------------------------
    # Options #

    -j, --jobs                                     Number of jobs. Defaults to all available.
    -b, --branch                                   Branch for the source repositories.
    --keep-output                                  If set, output sent through the terminal won't substitute lines, looking more like the log.

Example 1: ./xmipp
Example 2: ./xmipp all
Example 3: ./xmipp -j 20
Example 4: ./xmipp -b devel
Example 5: ./xmipp all -j 20 -b devel
""",
  terminal_sizes.SHORT_TERMINAL_WIDTH: f"""Default param. Runs config, configBuild, and compileAndInstall.

{NOTE_MESSAGE}Usage: xmipp all [options]
    ---------------------------------------------
    # Options #

    -j, --jobs                                     Number of jobs. Defaults
                                                   to all available.
    -b, --branch                                   Branch for the source
                                                   repositories.
    --keep-output                                  If set, output sent
                                                   through the terminal
                                                   won't substitute lines,
                                                   looking more like the
                                                   log.

Example 1: ./xmipp
Example 2: ./xmipp all
Example 3: ./xmipp -j 20
Example 4: ./xmipp -b devel
Example 5: ./xmipp all -j 20 -b devel
"""
}
