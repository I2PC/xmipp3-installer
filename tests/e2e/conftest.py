import subprocess
import sys
from unittest.mock import patch

import pytest

from xmipp3_installer.installer.handlers import shell_handler


@pytest.fixture(autouse=True)
def _fix_py_script_invocation_on_windows():
	if sys.platform != "win32":
		yield
		return
	_real_popen = subprocess.Popen
	def _patched_popen(cmd, *args, **kwargs):
		if isinstance(cmd, str) and cmd.split(None, 1)[0].endswith(".py"):
			cmd = f"python {cmd}"
		return _real_popen(cmd, *args, **kwargs)
	with patch.object(subprocess, "Popen", side_effect=_patched_popen):
		yield


@pytest.fixture(autouse=True)
def _fix_bash_invocation_on_windows():
	if sys.platform != "win32":
		yield
		return
	_real_run = shell_handler.run_shell_command
	def _patched_run(cmd, *args, **kwargs):
		if isinstance(cmd, str) and "bash" in cmd and "source" in cmd:
			return 0, ""
		return _real_run(cmd, *args, **kwargs)
	with patch.object(shell_handler, "run_shell_command", side_effect=_patched_run):
		yield
