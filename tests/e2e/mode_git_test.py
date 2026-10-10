import os
import subprocess

import pytest

from xmipp3_installer.application.cli.arguments import modes
from xmipp3_installer.installer import constants
from xmipp3_installer.installer.constants import paths

from . import init_git_repository
from .shell_command_outputs import mode_git
from .. import get_assertion_message, create_versions_json_file


@pytest.mark.parametrize(
  "__setup_evironment",
  [
    pytest.param(
      (False, False, False),
      id="Without xmipp, without xmippCore, without xmippViz"
    ),
    pytest.param(
      (False, False, True),
      id="Without xmipp, without xmippCore, with xmippViz"
    ),
    pytest.param(
      (False, True, False),
      id="Without xmipp, with xmippCore, without xmippViz"
    ),
    pytest.param(
      (False, True, True),
      id="Without xmipp, with xmippCore, with xmippViz"
    ),
    pytest.param(
      (True, False, False),
      id="With xmipp, without xmippCore, without xmippViz"
    ),
    pytest.param(
      (True, False, True),
      id="With xmipp, without xmippCore, with xmippViz"
    ),
    pytest.param(
      (True, True, False),
      id="With xmipp, with xmippCore, without xmippViz"
    ),
    pytest.param(
      (True, True, True),
      id="With xmipp, with xmippCore, with xmippViz"
    ),
  ],
  indirect=["__setup_evironment"]
)
def test_returns_returns_xpected_git_command_output(
  __setup_evironment,
):
  command_words = ["xmipp3_installer", modes.MODE_GIT, "branch"]
  result = subprocess.run(
    command_words,
    capture_output=True,
    text=True,
    check=False
  ).stdout
  expected_output = mode_git.get_git_command(*__setup_evironment)
  assert (
    result == expected_output
  ), get_assertion_message("git command output", expected_output, result)

@pytest.fixture
def __setup_evironment(request):
  sources_exist = getattr(request, 'param', (False, False, False))
  create_versions_json_file()
  init_git_repository()
  for exists, source in zip(sources_exist, [constants.XMIPP, *constants.XMIPP_SOURCES]):
    if exists:
      os.makedirs(os.path.join(paths.SOURCES_PATH, source))
  return sources_exist
