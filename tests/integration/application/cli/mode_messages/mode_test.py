from .. import terminal_sizes
from . import NOTE_MESSAGE

HELP_MESSAGE = {
  terminal_sizes.LARGE_TERMINAL_WIDTH: f"""Runs a given test.

{NOTE_MESSAGE}Usage: xmipp test [options]
    ---------------------------------------------
    # Options #

    testNames                                      Name of the tests to run. If combined with --show, greps the test names from the test list.
    --show                                         Shows the tests available and how to invoke those.
    --allPrograms                                  Runs the tests available for all programs.
    --allFuncs                                     Runs the tests available for all functions.

Example 1: ./xmipp test xmipp_sample_test
Example 2: ./xmipp test --short
Example 3: ./xmipp test --allPrograms
Example 4: ./xmipp test --allFuncs


""",
  terminal_sizes.SHORT_TERMINAL_WIDTH: f"""Runs a given test.

{NOTE_MESSAGE}Usage: xmipp test [options]
    ---------------------------------------------
    # Options #

    testNames                                      Name of the tests to run.
                                                   If combined with --show,
                                                   greps the test names from
                                                   the test list.
    --show                                         Shows the tests available
                                                   and how to invoke those.
    --allPrograms                                  Runs the tests available
                                                   for all programs.
    --allFuncs                                     Runs the tests available
                                                   for all functions.
Example 1: ./xmipp test xmipp_sample_test
Example 2: ./xmipp test --short
Example 3: ./xmipp test --allPrograms
Example 4: ./xmipp test --allFuncs
"""
}
