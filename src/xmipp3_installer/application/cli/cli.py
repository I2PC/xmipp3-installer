"""### Command Line Interface that interacts with the installer."""

import argparse
import multiprocessing
import os
import sys
from typing import Dict, Any

from xmipp3_installer.application.cli import arguments
from xmipp3_installer.application.cli.arguments import modes, params
from xmipp3_installer.application.cli.parsers import format
from xmipp3_installer.application.cli.parsers.error_handler_parser import ErrorHandlerArgumentParser
from xmipp3_installer.application.cli.parsers.general_help_formatter import GeneralHelpFormatter
from xmipp3_installer.application.cli.parsers.mode_help_formatter import ModeHelpFormatter
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer import installer_service

def main():
  """### Main entry point function that starts the execution."""
  parser = __generate_parser()
  parser = __add_params(parser)
  __add_default_usage_mode()
  args = vars(parser.parse_args())
  __validate_args(args, parser)
  installation_manager = installer_service.InstallationManager(args)
  ret_code = installation_manager.run_installer()
  sys.exit(ret_code)

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

def __add_params(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
  """
  ### Inserts the params into the given parser.

  #### Params:
  - parser (ArgumentParser): Argument parser.

  #### Returns:
  - (ArgumentParser): Argument parser with inserted params.
  """
  subparsers = parser.add_subparsers(dest=modes.MODE)
  default_jobs = __get_default_job_number()

  add_model_subparser = subparsers.add_parser(modes.MODE_ADD_MODEL, formatter_class=ModeHelpFormatter)
  __add_params_mode_add_model(add_model_subparser)

  all_subparser = subparsers.add_parser(modes.MODE_ALL, formatter_class=ModeHelpFormatter)
  __add_params_mode_all(all_subparser, default_jobs)

  subparsers.add_parser(modes.MODE_CLEAN_ALL, formatter_class=ModeHelpFormatter)

  subparsers.add_parser(modes.MODE_CLEAN_BIN, formatter_class=ModeHelpFormatter)

  compile_and_install_subparser = subparsers.add_parser(modes.MODE_COMPILE_AND_INSTALL, formatter_class=ModeHelpFormatter)
  __add_params_mode_compile_and_install(compile_and_install_subparser, default_jobs)

  build_config_subparser = subparsers.add_parser(modes.MODE_CONFIG_BUILD, formatter_class=ModeHelpFormatter)
  __add_params_mode_config_build(build_config_subparser)

  config_subparser = subparsers.add_parser(modes.MODE_CONFIG, formatter_class=ModeHelpFormatter)
  __add_params_mode_config(config_subparser)

  get_models_subparser = subparsers.add_parser(modes.MODE_GET_MODELS, formatter_class=ModeHelpFormatter)
  __add_params_mode_get_models(get_models_subparser)

  get_sources_subparser = subparsers.add_parser(modes.MODE_GET_SOURCES, formatter_class=ModeHelpFormatter)
  __add_params_mode_get_sources(get_sources_subparser)

  git_subparser = subparsers.add_parser(modes.MODE_GIT, formatter_class=ModeHelpFormatter)
  __add_params_mode_git(git_subparser)

  test_subparser = subparsers.add_parser(modes.MODE_TEST, formatter_class=ModeHelpFormatter)
  __add_params_mode_test(test_subparser)

  version_subparser = subparsers.add_parser(modes.MODE_VERSION, formatter_class=ModeHelpFormatter)
  __add_params_mode_version(version_subparser)

  return parser

def __add_params_mode_add_model(subparser: argparse.ArgumentParser):
  """
  ### Adds params for mode "addModel".

  #### Params:
  - subparser (ArgumentParser): Subparser to add the params to.
  """
  subparser.add_argument(*format.get_param_names(params.PARAM_LOGIN))
  subparser.add_argument(*format.get_param_names(params.PARAM_MODEL_PATH))
  subparser.add_argument(*format.get_param_names(params.PARAM_UPDATE), action='store_true')

def __add_params_mode_all(subparser: argparse.ArgumentParser, default_jobs: int):
  """
  ### Adds params for mode "all".

  #### Params:
  - subparser (ArgumentParser): Subparser to add the params to.
  - default_jobs (int): Default number of jobs to run the task.
  """
  subparser.add_argument(*format.get_param_names(params.PARAM_JOBS), type=int, default=default_jobs)
  subparser.add_argument(*format.get_param_names(params.PARAM_BRANCH))
  subparser.add_argument(*format.get_param_names(params.PARAM_KEEP_OUTPUT), action='store_true')

def __add_params_mode_compile_and_install(subparser: argparse.ArgumentParser, default_jobs: int):
  """
  ### Adds params for mode "compileAndInstall".

  #### Params:
  - subparser (ArgumentParser): Subparser to add the params to.
  - default_jobs (int): Default number of jobs to run the task.
  """
  subparser.add_argument(*format.get_param_names(params.PARAM_JOBS), type=int, default=default_jobs)
  subparser.add_argument(*format.get_param_names(params.PARAM_BRANCH))
  subparser.add_argument(*format.get_param_names(params.PARAM_KEEP_OUTPUT), action='store_true')

def __add_params_mode_config_build(subparser: argparse.ArgumentParser):
  """
  ### Adds params for mode "configBuild".

  #### Params:
  - subparser (ArgumentParser): Subparser to add the params to.
  """
  subparser.add_argument(*format.get_param_names(params.PARAM_KEEP_OUTPUT), action='store_true')

def __add_params_mode_config(subparser: argparse.ArgumentParser):
  """
  ### Adds params for mode "config".

  #### Params:
  - subparser (ArgumentParser): Subparser to add the params to.
  """
  subparser.add_argument(*format.get_param_names(params.PARAM_OVERWRITE), action='store_true')

def __add_params_mode_get_models(subparser: argparse.ArgumentParser):
  """
  ### Adds params for mode "getModels".

  #### Params:
  - subparser (ArgumentParser): Subparser to add the params to.
  """
  subparser.add_argument(
    *format.get_param_names(params.PARAM_MODELS_DIRECTORY),
    default=os.path.abspath(arguments.DEFAULT_MODELS_DIR)
  )

def __add_params_mode_get_sources(subparser: argparse.ArgumentParser):
  """
  ### Adds params for mode "getSources".

  #### Params:
  - subparser (ArgumentParser): Subparser to add the params to.
  """
  subparser.add_argument(*format.get_param_names(params.PARAM_BRANCH))
  subparser.add_argument(*format.get_param_names(params.PARAM_KEEP_OUTPUT), action='store_true')

def __add_params_mode_git(subparser: argparse.ArgumentParser):
  """
  ### Adds params for mode "git".

  #### Params:
  - subparser (ArgumentParser): Subparser to add the params to.
  """
  subparser.add_argument(*format.get_param_names(params.PARAM_GIT_COMMAND), nargs='+')

def __add_params_mode_test(subparser: argparse.ArgumentParser):
  """
  ### Adds params for mode "test".

  #### Params:
  - subparser (ArgumentParser): Subparser to add the params to.
  """
  group = subparser.add_mutually_exclusive_group(required=True)
  group.add_argument(*format.get_param_names(params.PARAM_TEST_NAMES), nargs='*', default=[])
  group.add_argument(*format.get_param_names(params.PARAM_SHOW_TESTS), action='store_true')
  group.add_argument(*format.get_param_names(params.PARAM_ALL_FUNCTIONS), action='store_true')
  group.add_argument(*format.get_param_names(params.PARAM_ALL_PROGRAMS), action='store_true')

def __add_params_mode_version(subparser: argparse.ArgumentParser):
  """
  ### Adds params for mode "version".

  #### Params:
  - subparser (ArgumentParser): Subparser to add the params to.
  """
  subparser.add_argument(*format.get_param_names(params.PARAM_SHORT), action='store_true')

def __get_default_job_number() -> int:
  """
  ### Gets the default number of jobs to be used by parallelizable tasks.

  Returned number will be 120% of CPU cores, due to not all jobs taking 
  100% of CPU time continuously.

  #### Returns:
  - (int): Default number of jobs.
  """
  return multiprocessing.cpu_count() + int(multiprocessing.cpu_count() * 0.2)

def __add_default_usage_mode():
  """### Sets the usage mode as the default one when a mode has not been specifically provided."""
  no_args_provided = len(sys.argv) == 1
  args_provided = len(sys.argv) > 1
  if no_args_provided or (
    args_provided and __is_first_arg_optional() and not __help_requested()
    ): 
    sys.argv.insert(1, modes.MODE_ALL)

def __is_first_arg_optional() -> bool:
  """
  ### Returns True if the first argument provided is optional.

  #### Returns:
  - (bool): True if the first argument received is optional.
  """
  return sys.argv[1].startswith('-')

def __help_requested() -> bool:
  """
  ### Returns True if help is at least one of the args.

  #### Returns:
  - (bool): True if help is at least one of the args.
  """
  return '-h' in sys.argv or '--help' in sys.argv

def __validate_args(args: Dict[str, Any], parser: argparse.ArgumentParser):
  """
  ### Performs validations on the arguments.

  #### Params:
  - args (dict(str, any)): Arguments to be validated.
  - parser (ArgumentParser): Argument parser.
  """
  jobs = args.get('jobs', 1)
  if jobs < 1:
    parser.error(f"Wrong job number \"{jobs}\". Number of jobs has to be 1 or greater.")
  
  branch = args.get('branch')
  if branch is not None and len(branch.split(' ')) > 1:
    parser.error(f"Incorrect branch name \"{branch}\". Branch names can only be one word long.")
  
  if args.get('keep_output', False):
    logger.set_allow_substitution(False)
