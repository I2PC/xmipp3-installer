from unittest.mock import patch, mock_open

import pytest

from xmipp3_installer.repository import config

from ... import get_assertion_message

__PATH = "/path/to/config.conf"
__FILE_LINES = ["line1\n", "line2\n", "line3\n"]

def test_calls_open_when_getting_file_content(__mock_path_exists, __mock_open):
	config.__get_file_content(__PATH)
	__mock_open.assert_called_once_with(__PATH, "r")

def test_calls_file_readlines_when_getting_file_content(__mock_path_exists, __mock_open):
	config.__get_file_content(__PATH)
	__mock_open().readlines.assert_called_once_with()

@pytest.mark.parametrize(
	"__mock_path_exists,__mock_open,expected_content",
	[
		pytest.param(False, [], []),
		pytest.param(False, __FILE_LINES, []),
		pytest.param(True, [], []),
		pytest.param(True, __FILE_LINES, __FILE_LINES)
	],
	indirect=["__mock_path_exists", "__mock_open"]
)
def test_returns_expected_file_content(
	__mock_path_exists,
	__mock_open,
	expected_content
):
	content = config.__get_file_content(__PATH)
	assert (
		content == expected_content
	), get_assertion_message("file content", expected_content, content)

@pytest.fixture(params=[True])
def __mock_path_exists(request):
	with patch("os.path.exists") as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(params=[__FILE_LINES])
def __mock_open(request):
  m_open = mock_open(read_data=''.join(request.param))
  with patch("builtins.open", m_open):
    yield m_open
