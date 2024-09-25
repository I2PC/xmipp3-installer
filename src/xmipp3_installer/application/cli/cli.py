"""### Command Line Interface that interacts with the installer."""

import argparse

def main():
	"""### Main entry point function that starts the execution."""
	parser = __generate_parser()
	parser = __add_params(parser)
	args = __get_args_from_parser(parser)
	test_service.test_scipion_plugin(args)

def __generate_parser() -> argparse.ArgumentParser:
	"""
	### Generates an argument parser for the installer.

	#### Returns:
	- (ArgumentParser): Argument parser.
	"""
	epilog = "Example 1: python -m scipion-testrunner /path/to/scipion myModule -j 2"
	epilog += f"\nExample 2: python -m scipion-testrunner /path/to/scipion myModule --{test_service.NO_GPU_PARAM_NAME}"
	return argparse.ArgumentParser(
			prog="scipion_testrunner",
			epilog=epilog,
			formatter_class=argparse.RawDescriptionHelpFormatter,
	)
