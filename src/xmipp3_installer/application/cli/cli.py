"""### Command Line Interface that interacts with the installer."""

import argparse

from xmipp3_installer.application.cli import arguments
from xmipp3_installer.application.cli.parsers.error_handler_parser import ErrorHandlerArgumentParser
from xmipp3_installer.application.cli.parsers.general_help_formatter import GeneralHelpFormatter

def main():
	"""### Main entry point function that starts the execution."""
	parser = __generate_parser()
	#parser = __add_params(parser)
	#args = __get_args_from_parser(parser)
	#test_service.test_scipion_plugin(args)

def __generate_parser() -> argparse.ArgumentParser:
	"""
	### Generates an argument parser for the installer.

	#### Returns:
	- (ArgumentParser): Argument parser.
	"""
	return ErrorHandlerArgumentParser(
		prog=arguments.XMIPP_PROGRAM_NAME,
		formatter_class=GeneralHelpFormatter,
	)

#def __add_params(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
#	"""
#	### Inserts the params into the given parser.
#
#	#### Params:
#	- parser (ArgumentParser): Argument parser.
#
#	#### Returns:
#	- (ArgumentParser): Argument parser with inserted params.
#	"""
#	subparsers = parser.add_subparsers(dest="mode")
#
#	# Arguments for mode 'addModel'
#	add_model_subparser = subparsers.add_parser(MODE_ADD_MODEL, formatter_class=custom_parser.ModeHelpFormatter)
#	add_model_subparser.add_argument(*getParamNames(PARAM_LOGIN))
#	add_model_subparser.add_argument(*getParamNames(PARAM_MODEL_PATH))
#	add_model_subparser.add_argument(*getParamNames(PARAM_UPDATE), action='store_true')
#
#	# Arguments for mode 'all'
#	all_subparser = subparsers.add_parser(MODE_ALL, formatter_class=custom_parser.ModeHelpFormatter)
#	all_subparser.add_argument(*getParamNames(PARAM_JOBS), type=int, default=JOBS)
#	all_subparser.add_argument(*getParamNames(PARAM_BRANCH))
#	all_subparser.add_argument(*getParamNames(PARAM_KEEP_OUTPUT), action='store_true')
#
#	# Arguments for mode 'cleanAll'
#	clean_all_subparser = subparsers.add_parser(MODE_CLEAN_ALL, formatter_class=custom_parser.ModeHelpFormatter)
#
#	# Arguments for mode 'cleanBin'
#	clean_bin_subparser = subparsers.add_parser(MODE_CLEAN_BIN, formatter_class=custom_parser.ModeHelpFormatter)
#
#	# Arguments for mode 'compileAndInstall'
#	compile_and_install_subparser = subparsers.add_parser(MODE_COMPILE_AND_INSTALL, formatter_class=custom_parser.ModeHelpFormatter)
#	compile_and_install_subparser.add_argument(*getParamNames(PARAM_JOBS), type=int, default=JOBS)
#	compile_and_install_subparser.add_argument(*getParamNames(PARAM_BRANCH))
#	compile_and_install_subparser.add_argument(*getParamNames(PARAM_KEEP_OUTPUT), action='store_true')
#
#	# Arguments for mode 'configBuild'
#	buildConfigSubparser = subparsers.add_parser(MODE_CONFIG_BUILD, formatter_class=custom_parser.ModeHelpFormatter)
#	buildConfigSubparser.add_argument(*getParamNames(PARAM_KEEP_OUTPUT), action='store_true')
#
#	# Arguments for mode 'config'
#	configSubparser = subparsers.add_parser(MODE_CONFIG, formatter_class=custom_parser.ModeHelpFormatter)
#	configSubparser.add_argument(*getParamNames(PARAM_OVERWRITE), action='store_true')
#
#	# Arguments for mode 'getModels'
#	getModelsSubparser = subparsers.add_parser(MODE_GET_MODELS, formatter_class=custom_parser.ModeHelpFormatter)
#	getModelsSubparser.add_argument(*getParamNames(PARAM_MODELS_DIRECTORY), default=os.path.join(__getProjectRootDir(), DEFAULT_MODELS_DIR))
#
#	# Arguments for mode 'getSources'
#	getSourcesSubparser = subparsers.add_parser(MODE_GET_SOURCES, formatter_class=custom_parser.ModeHelpFormatter)
#	getSourcesSubparser.add_argument(*getParamNames(PARAM_BRANCH))
#	getSourcesSubparser.add_argument(*getParamNames(PARAM_KEEP_OUTPUT), action='store_true')
#
#	# Arguments for mode 'git'
#	gitSubparser = subparsers.add_parser(MODE_GIT, formatter_class=custom_parser.ModeHelpFormatter)
#	gitSubparser.add_argument(*getParamNames(PARAM_GIT_COMMAND), nargs='+')
#
#	# Arguments for mode 'test'
#	testSubparser = subparsers.add_parser(MODE_TEST, formatter_class=custom_parser.ModeHelpFormatter)
#	testSubparser.add_argument(*getParamNames(PARAM_TEST_NAME), nargs='?', default=None)
#	testSubparser.add_argument(*getParamNames(PARAM_SHOW_TESTS), action='store_true')
#
#	# Arguments for mode 'version'
#	versionSubparser = subparsers.add_parser(MODE_VERSION, formatter_class=custom_parser.ModeHelpFormatter)
#	versionSubparser.add_argument(*getParamNames(PARAM_SHORT), action='store_true')
#
#	return parser
