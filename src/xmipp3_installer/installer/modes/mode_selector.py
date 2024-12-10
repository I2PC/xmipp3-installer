from xmipp3_installer.application.cli.arguments import modes
from xmipp3_installer.installer.modes import mode_config

MODE_FUNCTIONS = {
  modes.MODE_ADD_MODEL: NotImplemented,
  modes.MODE_ALL: NotImplemented,
  modes.MODE_CLEAN_ALL: NotImplemented,
  modes.MODE_CLEAN_BIN: NotImplemented,
  modes.MODE_COMPILE_AND_INSTALL: NotImplemented,
  modes.MODE_CONFIG_BUILD: NotImplemented,
  modes.MODE_CONFIG: mode_config.mode_config,
  modes.MODE_GET_MODELS: NotImplemented,
  modes.MODE_GET_SOURCES: NotImplemented,
  modes.MODE_GIT: NotImplemented,
  modes.MODE_TEST: NotImplemented,
  modes.MODE_VERSION: NotImplemented
}
