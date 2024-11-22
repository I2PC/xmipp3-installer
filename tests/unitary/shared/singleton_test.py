from unittest.mock import patch

import pytest

from xmipp3_installer.shared.singleton import Singleton

from ... import get_assertion_message

def test_returns_new_instance():
	singleton1 = Singleton()
	with patch.object(Singleton, "_Singleton__instance", None):
		singleton2 = Singleton()
	assert (
		singleton1 is not singleton2
	), "Received same singleton instance, when should have been different."

def test_returns_same_instance():
	singleton1 = Singleton()
	singleton2 = Singleton()
	assert (
		singleton1 is singleton2
	), get_assertion_message("Singleton instance", singleton1, singleton2)
