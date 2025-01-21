"""### Containis all param constants needed for the argument parsing part of Xmipp's installation."""

from xmipp3_installer.application.cli.arguments import DEFAULT_BUILD_DIR

# Definition of all params found in the
SHORT_VERSION = 'short'
LONG_VERSION = 'long'
DESCRIPTION = 'description'

# Possible param list
PARAM_SHORT = 'short'
PARAM_JOBS = 'jobs'
PARAM_BRANCH = 'branch'
PARAM_MODELS_DIRECTORY = 'models-directory'
PARAM_TEST_NAME = 'testName'
PARAM_SHOW_TESTS = 'show-tests'
PARAM_GIT_COMMAND = 'git-command'
PARAM_LOGIN = 'login'
PARAM_MODEL_PATH = 'modelPath'
PARAM_UPDATE = 'update'
PARAM_OVERWRITE = 'overwrite'
PARAM_KEEP_OUTPUT = "keep-output"
PARAMS = {
	PARAM_SHORT: {
		LONG_VERSION: "--short",
		DESCRIPTION: "If set, only version number is shown."
	},
	PARAM_JOBS: {
		SHORT_VERSION: "-j",
		LONG_VERSION: "--jobs",
		DESCRIPTION: "Number of jobs. Defaults to all available."
	},
	PARAM_BRANCH: {
		SHORT_VERSION: "-b",
		LONG_VERSION: "--branch",
		DESCRIPTION: "Branch for the source repositories."
	},
	PARAM_MODELS_DIRECTORY: {
		SHORT_VERSION: "-d",
		LONG_VERSION: "--directory",
		DESCRIPTION: f"Directory where models will be saved. Default is \"{DEFAULT_BUILD_DIR}\"."
	},
	PARAM_TEST_NAME: {
		SHORT_VERSION: PARAM_TEST_NAME,
		DESCRIPTION: "Run certain test. If combined with --show, greps the test name from the test list."
	},
	PARAM_SHOW_TESTS: {
		LONG_VERSION: "--show",
		DESCRIPTION: "Shows the tests available and how to invoke those."
	},
	PARAM_GIT_COMMAND: {
		SHORT_VERSION: "command",
		DESCRIPTION: "Git command to run on all source repositories."
	},
	PARAM_LOGIN: {
		SHORT_VERSION: "login",
		DESCRIPTION: "Login (usr@server) for remote host to upload the model with. Must have write permisions to such machine."
	},
	PARAM_MODEL_PATH: {
		SHORT_VERSION: PARAM_MODEL_PATH,
		DESCRIPTION: "Path to the model to upload to remote host."
	},
	PARAM_UPDATE: {
		LONG_VERSION: "--update",
		DESCRIPTION: "Flag to update an existing model"
	},
	PARAM_OVERWRITE: {
		SHORT_VERSION: "-o",
		LONG_VERSION: "--overwrite",
		DESCRIPTION: "If set, current config file will be overwritten with a new one."
	},
	PARAM_KEEP_OUTPUT: {
		LONG_VERSION: "--keep-output",
		DESCRIPTION: "If set, output sent through the terminal won't substitute lines, looking more like the log."
	}
}
