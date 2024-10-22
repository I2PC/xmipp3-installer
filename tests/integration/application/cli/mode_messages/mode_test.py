from .. import terminal_sizes
from . import NOTE_MESSAGE

HELP_MESSAGE = {
  terminal_sizes.LARGE_TERMINAL_WIDTH: f"""Runs a given test.

{NOTE_MESSAGE}Usage: xmipp test [options]
    ---------------------------------------------
    # Options #

    testName                                       Run certain test. If combined with --show, greps the test name from the test list.
    --show                                         Shows the tests available and how to invoke those.

Example 1: ./xmipp test xmipp_sample_test
Example 2: ./xmipp test --short
""",
  terminal_sizes.SHORT_TERMINAL_WIDTH: f"""Runs a given test.

{NOTE_MESSAGE}Usage: xmipp test [options]
    ---------------------------------------------
    # Options #

    testName                                       Run certain test. If
                                                   combined with --show,
                                                   greps the test name from
                                                   the test list.
    --show                                         Shows the tests available
                                                   and how to invoke those.

Example 1: ./xmipp test xmipp_sample_test
Example 2: ./xmipp test --short
"""
}
