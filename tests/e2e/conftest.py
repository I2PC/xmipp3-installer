import subprocess
import sys
from unittest.mock import patch

import pytest


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
