from .. import terminal_sizes
from . import NOTE_MESSAGE

HELP_MESSAGE = {
  terminal_sizes.LARGE_TERMINAL_WIDTH: f"""Downloads the Deep Learning Models required by the DLTK tools at dir/models (dist by default).
Visit https://i2pc.github.io/docs/Installation/Optionals/index.html#deeplearningtoolkit for more details.

{NOTE_MESSAGE}Usage: xmipp getModels [options]
    --------------------------------------------------------------------
    # Options #

    -d, --directory                                                       Directory where models will be saved. Default is "dist".

Example 1: ./xmipp getModels
Example 2: ./xmipp getModels -d /path/to/my/model/directory
""",
  terminal_sizes.SHORT_TERMINAL_WIDTH: f"""Downloads the Deep Learning Models required by the DLTK tools at dir/models (dist by default).
Visit https://i2pc.github.io/docs/Installation/Optionals/index.html#deeplearningtoolkit for more details.

{NOTE_MESSAGE}Usage: xmipp getModels [options]
    --------------------------------------------------------------------
    # Options #

    -d, --directory                                                       Directory where models will be saved.
                                                                          Default is "dist".

Example 1: ./xmipp getModels
Example 2: ./xmipp getModels -d /path/to/my/model/directory
"""
}
