import os
import subprocess

import pytest

from xmipp3_installer.application.cli.arguments import modes
from xmipp3_installer.installer.constants import paths

from . import get_source_paths, init_git_repository
from .shell_command_outputs import mode_version
from .. import (
  get_assertion_message, copy_file_from_reference,
  get_test_file, create_versions_json_file, JSON_XMIPP_VERSION_NAME
)

def test_returns_short_version(__setup_evironment):
  command_words = ["xmipp3_installer", modes.MODE_VERSION, "--short"]
  result = subprocess.run(
    command_words,
    capture_output=True,
    text=True,
    check=False
  ).stdout
  expected_version = f"{JSON_XMIPP_VERSION_NAME}\n"
  assert (
    result == expected_version
  ), get_assertion_message("short version", expected_version, result)

@pytest.mark.parametrize(
  "__setup_evironment,expected_output_function",
  [
    pytest.param((False, False), mode_version.get_full_info_before_config, id="Before config without sources"),
    pytest.param((False, True), mode_version.get_full_info_before_config_with_sources, id="Before config with sources"),
    pytest.param((True, False), mode_version.get_full_info_after_config_without_sources, id="After config without sources"),
    pytest.param((True, True), mode_version.get_full_info_after_config_with_sources, id="After config with sources")
  ],
  indirect=["__setup_evironment"]
)
def test_returns_full_version(
  __setup_evironment,
  expected_output_function
):
  command_words = ["xmipp3_installer", modes.MODE_VERSION]
  result = subprocess.run(
    command_words,
    capture_output=True,
    text=True,
    check=False
  ).stdout
  expected_output = expected_output_function()
  assert (
    result == expected_output
  ), get_assertion_message("full version", expected_output, result)

@pytest.fixture
def __setup_evironment(request):
  config_done, sources_exist = getattr(request, 'param', (False, False))
  create_versions_json_file()
  init_git_repository()
  if config_done:
    copy_file_from_reference(
      get_test_file("libraries-with-versions.txt"),
      paths.LIBRARY_VERSIONS_FILE
    )
    copy_file_from_reference(
      get_test_file(os.path.join("conf-files", "input", "default.conf")),
      paths.CONFIG_FILE
    )
  if sources_exist:
    for source in get_source_paths():
      os.makedirs(source)
  return config_done, sources_exist
