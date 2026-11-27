import os
import subprocess
from unittest.mock import patch

from xmipp3_installer.installer.handlers import conda_handler

from .... import get_assertion_message

def test_sets_variables_from_activation_scripts_when_reactivating_environment(tmp_path):
  conda_executable = tmp_path / "my conda" / "conda"
  conda_executable.parent.mkdir()
  conda_executable.write_text(
    "#!/bin/sh\necho \"export CC='x86_64-conda-linux-gnu-cc'; export FLAGS='-a -b=c'\"\n",
    encoding="utf-8"
  )
  conda_executable.chmod(0o755)
  with patch.dict('os.environ', {"OLD": "value"}):
    is_reactivated = conda_handler.reactivate_environment(str(conda_executable))
    values = (is_reactivated, os.environ.get("CC"), os.environ.get("FLAGS"), os.environ.get("OLD"))
  expected_values = (True, "x86_64-conda-linux-gnu-cc", "-a -b=c", "value")
  assert (
    values == expected_values
  ), get_assertion_message("reactivation values", expected_values, values)

def test_does_not_run_injected_commands_when_running_environment_update_command(tmp_path):
  conda_executable = tmp_path / "my conda" / "conda"
  conda_executable.parent.mkdir()
  conda_executable.write_text('#!/bin/sh\nprintf "%s\\n" "$@"\n', encoding="utf-8")
  conda_executable.chmod(0o755)
  command = conda_handler.get_environment_update_command(
    str(conda_executable), '/envs/"$(touch pwned)"', "conda/`touch pwned`.yml"
  )
  output = subprocess.run(
    command, shell=True, cwd=tmp_path, capture_output=True, text=True, check=True
  ).stdout.splitlines()
  values = (output, (tmp_path / "pwned").exists())
  expected_values = (
    ["env", "update", "--prefix", '/envs/"$(touch pwned)"', "--file", "conda/`touch pwned`.yml"],
    False
  )
  assert (
    values == expected_values
  ), get_assertion_message("arguments and injection", expected_values, values)
