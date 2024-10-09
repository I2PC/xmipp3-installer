from unittest.mock import patch

import pytest

from xmipp3_installer.application.cli.parsers import format
from xmipp3_installer.application.cli import arguments

__PARAMS = {
	"test1": {
		arguments.SHORT_VERSION: "short_name",
		arguments.LONG_VERSION: "long_name"
	},
	"test2": {
		arguments.LONG_VERSION: "long_name"
	},
	"test3": {
		arguments.SHORT_VERSION: "short_name"
	},
	"test4": {},
	"test5": {
		arguments.SHORT_VERSION: "short_name",
		arguments.LONG_VERSION: "long_name",
		"non-needed-key": "whatever"
	},
}

@pytest.mark.parametrize(
	"tab_size",
	[
		pytest.param(4),
		pytest.param(0),
		pytest.param(1),
		pytest.param(-1),
	],
)
def test_expands_tabs_with_expected_length(tab_size):
	with patch.object(format, "TAB_SIZE", tab_size):
		assert (
			len(format.get_formatting_tabs("		")) == 2*tab_size
		), "Received text with different length than expected."

@pytest.mark.parametrize(
	"key,expected_n_names",
	[
		pytest.param("test1", 2),
		pytest.param("test2", 1),
		pytest.param("test3", 1),
		pytest.param("test4", 0),
		pytest.param("test5", 2)
	],
)
def test_gets_expected_param_names(key, expected_n_names):
	with patch.object(arguments, "PARAMS", __PARAMS):
		assert (
			len(format.get_param_names(key)) == expected_n_names
		), "Received different amount of names than expected."
