from xmipp3_installer.application.logger.logger import logger

from . import terminal_sizes

__NOTE_MESSAGE = logger.yellow(
  'Note: You can also view a specific help message for each mode with "./xmipp [mode] -h".\nExample: ./xmipp all -h\n'
)

HELP_MESSAGE = {
  terminal_sizes.LARGE_TERMINAL_WIDTH: f"""Run Xmipp\'s installer script

Usage: xmipp [options]
    --------------------------------------------------------------------
    # General #

    version [--short]                                                     Returns the version information. Add \'--short\' to print only the version number.
    compileAndInstall [-j] [--keep-output]                                Compiles and installs Xmipp based on already obtained sources.
    all [-j] [-b] [--keep-output]                                         Default param. Runs config, configBuild, and compileAndInstall.
    configBuild [--keep-output]                                           Configures the project with CMake.
    --------------------------------------------------------------------
    # Config #

    config [-o]                                                           Generates a config file template with default values.
    --------------------------------------------------------------------
    # Downloads #

    getModels [-d]                                                        Downloads the Deep Learning Models required by the DLTK tools at dir/models (dist by default).
    getSources [-b] [--keep-output]                                       Clone all Xmipp\'s sources.
    --------------------------------------------------------------------
    # Clean #

    cleanBin                                                              Removes all compiled binaries.
    cleanAll                                                              Removes all compiled binaries and sources, leaves the repository as if freshly cloned (without pulling).
    --------------------------------------------------------------------
    # Test #

    test ([testNames] | [--show] | [--all-functions] | [--all-programs])  Runs Xmipp\'s tests.
    --------------------------------------------------------------------
    # Developers #

    git [command]                                                         Runs the given git action for all source repositories.
    addModel [login] [modelPath] [--update]                               Takes a DeepLearning model from the modelPath, makes a tgz of it and uploads the .tgz according to the <login>.

Example 1: ./xmipp
Example 2: ./xmipp compileAndInstall -j 4
{__NOTE_MESSAGE}""",
  terminal_sizes.SHORT_TERMINAL_WIDTH: f"""Run Xmipp\'s installer script

Usage: xmipp [options]
    --------------------------------------------------------------------
    # General #

    version [--short]                                                     Returns the version information. Add
                                                                          \'--short\' to print only the version
                                                                          number.
    compileAndInstall [-j] [--keep-output]                                Compiles and installs Xmipp based on
                                                                          already obtained sources.
    all [-j] [-b] [--keep-output]                                         Default param. Runs config,
                                                                          configBuild, and compileAndInstall.
    configBuild [--keep-output]                                           Configures the project with CMake.
    --------------------------------------------------------------------
    # Config #

    config [-o]                                                           Generates a config file template with
                                                                          default values.
    --------------------------------------------------------------------
    # Downloads #

    getModels [-d]                                                        Downloads the Deep Learning Models
                                                                          required by the DLTK tools at
                                                                          dir/models (dist by default).
    getSources [-b] [--keep-output]                                       Clone all Xmipp\'s sources.
    --------------------------------------------------------------------
    # Clean #

    cleanBin                                                              Removes all compiled binaries.
    cleanAll                                                              Removes all compiled binaries and
                                                                          sources, leaves the repository as if
                                                                          freshly cloned (without pulling).
    --------------------------------------------------------------------
    # Test #

    test ([testNames] | [--show] | [--all-functions] | [--all-programs])  Runs Xmipp\'s tests.
    --------------------------------------------------------------------
    # Developers #

    git [command]                                                         Runs the given git action for all
                                                                          source repositories.
    addModel [login] [modelPath] [--update]                               Takes a DeepLearning model from the
                                                                          modelPath, makes a tgz of it and
                                                                          uploads the .tgz according to the
                                                                          <login>.

Example 1: ./xmipp
Example 2: ./xmipp compileAndInstall -j 4
{__NOTE_MESSAGE}"""
}
