from xmipp3_installer.application.cli.arguments import modes
from xmipp3_installer.installer.modes import (
  mode_config_executor, mode_version_executor, mode_git_executor
)
from xmipp3_installer.installer.modes.mode_clean import mode_clean_all_executor, mode_clean_bin_executor
from xmipp3_installer.installer.modes.mode_models import mode_add_model_executor, mode_get_models_executor

MODE_EXECUTORS = {
  modes.MODE_ADD_MODEL: mode_add_model_executor.ModeAddModelExecutor,
  modes.MODE_ALL: NotImplemented,
  modes.MODE_CLEAN_ALL: mode_clean_all_executor.ModeCleanAllExecutor,
  modes.MODE_CLEAN_BIN: mode_clean_bin_executor.ModeCleanBinExecutor,
  modes.MODE_COMPILE_AND_INSTALL: NotImplemented,
  modes.MODE_CONFIG_BUILD: NotImplemented,
  modes.MODE_CONFIG: mode_config_executor.ModeConfigExecutor,
  modes.MODE_GET_MODELS: mode_get_models_executor.ModeGetModelsExecutor,
  modes.MODE_GET_SOURCES: NotImplemented,
  modes.MODE_GIT: mode_git_executor.ModeGitExecutor,
  modes.MODE_TEST: NotImplemented,
  modes.MODE_VERSION: mode_version_executor.ModeVersionExecutor
}
