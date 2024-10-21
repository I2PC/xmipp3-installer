from unittest.mock import patch

import pytest

from xmipp3_installer.application.cli.parsers import format
from xmipp3_installer.application.cli.arguments import params

from .... import get_assertion_message

__PARAMS = {
	"test1": {
		params.SHORT_VERSION: "short_name",
		params.LONG_VERSION: "long_name"
	},
	"test2": {
		params.LONG_VERSION: "long_name"
	},
	"test3": {
		params.SHORT_VERSION: "short_name"
	},
	"test4": {},
	"test5": {
		params.SHORT_VERSION: "short_name",
		params.LONG_VERSION: "long_name",
		"non-needed-key": "whatever"
	},
}

@pytest.mark.parametrize(
	"tab_size,expected_length",
	[
		pytest.param(4, 8),
		pytest.param(0, 0),
		pytest.param(1, 2),
		pytest.param(-1, 0)
	],
)
def test_expands_tabs_with_expected_length(tab_size, expected_length):
	with patch.object(format, "TAB_SIZE", tab_size):
		text_length = len(format.get_formatting_tabs("		"))
		assert (
			text_length == expected_length
		), get_assertion_message("text length", expected_length, text_length)

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
	with patch.object(params, "PARAMS", __PARAMS):
		name_amount = len(format.get_param_names(key))
		assert (
			name_amount == expected_n_names
		), get_assertion_message("name amount", expected_n_names, name_amount)
