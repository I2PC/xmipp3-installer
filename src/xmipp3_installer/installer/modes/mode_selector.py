"""
### Mode Selector Module.

This module maps command-line modes to their corresponding executor classes.
"""

from xmipp3_installer.application.cli.arguments import modes
from xmipp3_installer.installer.modes import (
  mode_config_executor, mode_version_executor, mode_git_executor,
  mode_get_sources_executor, mode_all_executor
)
from xmipp3_installer.installer.modes.mode_clean import mode_clean_all_executor, mode_clean_bin_executor
from xmipp3_installer.installer.modes.mode_sync import (
  mode_add_model_executor, mode_get_models_executor, mode_test_executor
)
from xmipp3_installer.installer.modes.mode_cmake import mode_config_build_executor, mode_compile_and_install_executor

MODE_EXECUTORS = {
  modes.MODE_ADD_MODEL: mode_add_model_executor.ModeAddModelExecutor,
  modes.MODE_ALL: mode_all_executor.ModeAllExecutor,
  modes.MODE_CLEAN_ALL: mode_clean_all_executor.ModeCleanAllExecutor,
  modes.MODE_CLEAN_BIN: mode_clean_bin_executor.ModeCleanBinExecutor,
  modes.MODE_COMPILE_AND_INSTALL: mode_compile_and_install_executor.ModeCompileAndInstallExecutor,
  modes.MODE_CONFIG_BUILD: mode_config_build_executor.ModeConfigBuildExecutor,
  modes.MODE_CONFIG: mode_config_executor.ModeConfigExecutor,
  modes.MODE_GET_MODELS: mode_get_models_executor.ModeGetModelsExecutor,
  modes.MODE_GET_SOURCES: mode_get_sources_executor.ModeGetSourcesExecutor,
  modes.MODE_GIT: mode_git_executor.ModeGitExecutor,
  modes.MODE_TEST: mode_test_executor.ModeTestExecutor,
  modes.MODE_VERSION: mode_version_executor.ModeVersionExecutor
}
