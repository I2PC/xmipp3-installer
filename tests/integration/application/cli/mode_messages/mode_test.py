from .. import terminal_sizes
from . import NOTE_MESSAGE

HELP_MESSAGE = {
  terminal_sizes.LARGE_TERMINAL_WIDTH: f"""Runs Xmipp's tests.
If used with 'testNames', only the tests provided will run.
If used with '--show', a list the tests available and how to invoke them will be shown.
If used with '--all-functions', all function tests will run.
If used with '--all-programs', all program tests will run.

\x1b[93mImportant: In this mode, there are mutually exclusive groups of params. You can only use from one of them at a time.
\x1b[0m{NOTE_MESSAGE}Usage: xmipp test [options]
    --------------------------------------------------------------------
    # Options #

    testNames                                                             Name of the tests to run.
    ---------------
    --show                                                                Shows the tests available and how to invoke those.
    ---------------
    --all-functions                                                       If set, all function tests will be run.
    ---------------
    --all-programs                                                        If set, all program tests will be run.

Example 1: ./xmipp test xmipp_sample_test
Example 2: ./xmipp test --show
Example 3: ./xmipp test --all-functions
Example 4: ./xmipp test --all-programs
""",
  terminal_sizes.SHORT_TERMINAL_WIDTH: f"""Runs Xmipp's tests.
If used with 'testNames', only the tests provided will run.
If used with '--show', a list the tests available and how to invoke them will be shown.
If used with '--all-functions', all function tests will run.
If used with '--all-programs', all program tests will run.

\x1b[93mImportant: In this mode, there are mutually exclusive groups of params. You can only use from one of them at a time.
\x1b[0m{NOTE_MESSAGE}Usage: xmipp test [options]
    --------------------------------------------------------------------
    # Options #

    testNames                                                             Name of the tests to run.
    ---------------
    --show                                                                Shows the tests available and how to
                                                                          invoke those.
    ---------------
    --all-functions                                                       If set, all function tests will be
                                                                          run.
    ---------------
    --all-programs                                                        If set, all program tests will be
                                                                          run.

Example 1: ./xmipp test xmipp_sample_test
Example 2: ./xmipp test --show
Example 3: ./xmipp test --all-functions
Example 4: ./xmipp test --all-programs
"""
}
