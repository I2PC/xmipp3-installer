from .. import terminal_sizes
from . import NOTE_MESSAGE

HELP_MESSAGE = {
  terminal_sizes.LARGE_TERMINAL_WIDTH: f"""Clones Xmipp\'s source repositories xmippCore & xmippViz.

{NOTE_MESSAGE}Usage: xmipp getSources [options]
    --------------------------------------------------------------------
    # Options #

    -b, --branch                                                          Branch for the source repositories.
    --keep-output                                                         If set, output sent through the terminal won't substitute lines, looking more like the log.

Example: ./xmipp getSources./xmipp getSources -b devel
""",
  terminal_sizes.SHORT_TERMINAL_WIDTH: f"""Clones Xmipp\'s source repositories xmippCore & xmippViz.

{NOTE_MESSAGE}Usage: xmipp getSources [options]
    --------------------------------------------------------------------
    # Options #

    -b, --branch                                                          Branch for the source repositories.
    --keep-output                                                         If set, output sent through the
                                                                          terminal won't substitute lines,
                                                                          looking more like the log.

Example: ./xmipp getSources./xmipp getSources -b devel
"""
}
