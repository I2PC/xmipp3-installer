from unittest.mock import patch, MagicMock, call

import pytest

from xmipp3_installer.installer import constants
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.installer.modes.mode_clean.mode_clean_bin_executor import ModeCleanBinExecutor
from xmipp3_installer.installer.modes.mode_clean.mode_clean_executor import ModeCleanExecutor

from ..... import get_assertion_message

def test_implements_interface_mode_clean_executor():
	executor = ModeCleanBinExecutor({})
	assert (
		isinstance(executor, ModeCleanExecutor)
	), get_assertion_message(
		"parent class",
		ModeCleanExecutor.__name__,
		executor.__class__.__bases__[0].__name__
	)

def test_does_not_override_parent_config_values(__dummy_test_mode_clean_executor):
	base_executor = __dummy_test_mode_clean_executor({})
	clean_bin_executor = ModeCleanBinExecutor({})
	base_config = (
		base_executor.logs_to_file,
		base_executor.prints_with_substitution,
		base_executor.prints_banner_on_exit,
		base_executor.sends_installation_info
	)
	inherited_config = (
		clean_bin_executor.logs_to_file,
		clean_bin_executor.prints_with_substitution,
		clean_bin_executor.prints_banner_on_exit,
		clean_bin_executor.sends_installation_info
	)
	assert (
		inherited_config == base_config
	), get_assertion_message("config values", base_config, inherited_config)

def test_returns_expected_confirmation_keyword():
	expected_keyword = "y"
	confirmation_keyword = ModeCleanBinExecutor({})._get_confirmation_keyword()
	assert (
		confirmation_keyword == expected_keyword
	), get_assertion_message("confirmation keyword", expected_keyword, confirmation_keyword)

def test_calls_get_confirmation_keyword_when_getting_confirmation_message(
	__mock_get_confirmation_keyword
):
	ModeCleanBinExecutor({})._get_confirmation_message()
	__mock_get_confirmation_keyword.assert_called_once_with()

def test_returns_expected_confirmation_message(
	__mock_get_confirmation_keyword,
	__mock_logger_yellow
):
	confirmation_message = ModeCleanBinExecutor({})._get_confirmation_message()
	expected_confirmation_message = __mock_logger_yellow(
		f"WARNING: This will DELETE from {paths.SOURCES_PATH} all *.so, *.os and *.o files. Also the *.pyc and *.dblite files"
	)
	second_line = __mock_logger_yellow(
		f"If you are sure you want to do this, type '{__mock_get_confirmation_keyword()}' (case sensitive):"
	)
	expected_confirmation_message += f"\n{second_line}"
	assert (
		confirmation_message == expected_confirmation_message
	), get_assertion_message("confirmation message", expected_confirmation_message, confirmation_message)

def test_calls_path_rglob_when_getting_pycache_dirs(
	__mock_path
):
	ModeCleanBinExecutor._ModeCleanBinExecutor__get_pycache_dirs()
	__mock_path().rglob.assert_called_once_with("__pycache__")
	
@pytest.mark.parametrize(
	"expected_dirs",
	[
		pytest.param([]),
		pytest.param(["/path/to/file1"]),
		pytest.param(["/path/to/file1", "/path/to/file2"])
	]
)
def test_returns_expected_pycache_dirs(__mock_path, expected_dirs):
	__mock_path().rglob.return_value = expected_dirs
	pycache_dirs = ModeCleanBinExecutor._ModeCleanBinExecutor__get_pycache_dirs()
	assert (
		pycache_dirs == expected_dirs
	), get_assertion_message("pycache dirs", expected_dirs, pycache_dirs)

def test_calls_os_walk_when_getting_empty_dirs(
	__mock_os_walk,
	__mock_os_path_join
):
	ModeCleanBinExecutor._ModeCleanBinExecutor__get_empty_dirs()
	__mock_os_walk.assert_called_once_with(
		__mock_os_path_join(
			paths.SOURCES_PATH,
			constants.XMIPP,
			"applications",
			"programs"
		)
	)

def test_returns_expected_empty_dirs(__mock_os_walk):
	__mock_os_walk.side_effect = None
	__mock_os_walk.return_value = [
		(paths.INSTALL_PATH, ["folder1", "folder2"], []),
		(f"{paths.INSTALL_PATH}/folder1", [], ["file1"]),
		(f"{paths.INSTALL_PATH}/folder2", ["subfolder1", "subfolder2"], []),
		(f"{paths.INSTALL_PATH}/folder2/subfolder1", [], []),
		(f"{paths.INSTALL_PATH}/folder2/subfolder2", ["empty"], []),
		(f"{paths.INSTALL_PATH}/folder2/subfolder2/empty", [], [])
	]
	expected_empty_dirs = [
		f"{paths.INSTALL_PATH}/folder2/subfolder1",
		f"{paths.INSTALL_PATH}/folder2/subfolder2/empty"
	]
	empty_dirs = ModeCleanBinExecutor._ModeCleanBinExecutor__get_empty_dirs()
	assert (
		empty_dirs == expected_empty_dirs
	), get_assertion_message("empty directories", expected_empty_dirs, empty_dirs)

def test_calls_os_walk_when_getting_compilation_files(__mock_os_walk):
	ModeCleanBinExecutor._ModeCleanBinExecutor__get_compilation_files()
	__mock_os_walk.assert_called_once_with(paths.SOURCES_PATH)

def test_calls_glob_when_getting_compilation_files(
	__mock_os_walk,
	__mock_fnmatch_filter
):
	__mock_os_walk.side_effect = None
	files = ["file1", "file2", "file3"]
	__mock_os_walk.return_value = [("root", [], files)]
	ModeCleanBinExecutor._ModeCleanBinExecutor__get_compilation_files()
	__mock_fnmatch_filter.assert_has_calls([
		call(files, '*.so'),
		call(files, '*.os'),
		call(files, '*.o')
	])
	assert (
		__mock_fnmatch_filter.call_count == 3
	), get_assertion_message("call count", 3, __mock_fnmatch_filter.call_count)

def test_returns_expected_compilation_files(
	__mock_fnmatch_filter,
	__mock_os_path_join
):
	__mock_fnmatch_filter.side_effect = [["file1"], ["file2", "file3"], ["file4"]]
	expected_compilation_files = [
		__mock_os_path_join(paths.SOURCES_PATH, file_name)
		for file_name in ["file1", "file2", "file3", "file4"]
	]
	compilation_files = ModeCleanBinExecutor._ModeCleanBinExecutor__get_compilation_files()
	assert (
		compilation_files == expected_compilation_files
	), get_assertion_message("compilation files", expected_compilation_files, compilation_files)

def test_calls_glob_when_getting_paths_to_delete(
	__mock_glob,
	__mock_get_compilation_files,
	__mock_get_empty_dirs,
	__mock_get_pycache_dirs
):
	ModeCleanBinExecutor({})._get_paths_to_delete()
	__mock_glob.assert_called_once_with("**/*.dblite", recursive=True)

def test_calls_get_compilation_files_when_getting_paths_to_delete(
	__mock_glob,
	__mock_get_compilation_files,
	__mock_get_empty_dirs,
	__mock_get_pycache_dirs
):
	ModeCleanBinExecutor({})._get_paths_to_delete()
	__mock_get_compilation_files.assert_called_once_with()

def test_calls_get_empty_dirs_when_getting_paths_to_delete(
	__mock_glob,
	__mock_get_compilation_files,
	__mock_get_empty_dirs,
	__mock_get_pycache_dirs
):
	ModeCleanBinExecutor({})._get_paths_to_delete()
	__mock_get_empty_dirs.assert_called_once_with()

def test_calls_get_pycache_dirs_when_getting_paths_to_delete(
	__mock_glob,
	__mock_get_compilation_files,
	__mock_get_empty_dirs,
	__mock_get_pycache_dirs
):
	ModeCleanBinExecutor({})._get_paths_to_delete()
	__mock_get_pycache_dirs.assert_called_once_with()

def test_returns_expected_paths_to_delete(
	__mock_glob,
	__mock_get_compilation_files,
	__mock_get_empty_dirs,
	__mock_get_pycache_dirs
):
	__mock_glob.return_value = ["globfile"]
	expected_paths_to_delete = [
		*__mock_glob(),
		*__mock_get_compilation_files(),
		*__mock_get_empty_dirs(),
		*__mock_get_pycache_dirs(),
		paths.BUILD_PATH
	]
	paths_to_delete = ModeCleanBinExecutor({})._get_paths_to_delete()
	assert (
		paths_to_delete == expected_paths_to_delete
	), get_assertion_message("paths to delete", expected_paths_to_delete, paths_to_delete)

@pytest.fixture
def __dummy_test_mode_clean_executor():
	class TestExecutor(ModeCleanExecutor):
		def _get_paths_to_delete(self):
			return []
		def _get_confirmation_message(self):
			return ""
		def _get_confirmation_keyword(self):
			return ""
	# For coverage
	executor = TestExecutor({})
	executor._get_paths_to_delete()
	executor._get_confirmation_message()
	executor._get_confirmation_keyword()
	return TestExecutor

@pytest.fixture
def __mock_get_confirmation_keyword():
	with patch(
		"xmipp3_installer.installer.modes.mode_clean.mode_clean_bin_executor.ModeCleanBinExecutor._get_confirmation_keyword"
	) as mock_method:
		mock_method.return_value = "confirmation keyword"
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_logger():
	with patch(
		"xmipp3_installer.application.logger.logger.Logger.__call__"
	) as mock_method:
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_logger_yellow():
	with patch(
		"xmipp3_installer.application.logger.logger.Logger.yellow"
	) as mock_method:
		mock_method.side_effect = lambda text: f"yellow-{text}-yellow"
		yield mock_method

@pytest.fixture(autouse=True, params=[True])
def __mock_get_user_confirmation(request):
	with patch(
		"xmipp3_installer.application.user_interactions.get_user_confirmation"
	) as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_path():
	new_path = MagicMock()
	new_path.rglob.return_value = ['/path/to/file1', '/path/to/file2']
	with patch("pathlib.Path") as mock_object:
		mock_object.return_value = new_path
		yield mock_object

@pytest.fixture(autouse=True)
def __mock_os_walk():
	with patch("os.walk") as mock_method:
		mock_method.side_effect = lambda root: [(root, [], [])]
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_os_path_join():
	def __join_with_foward_slashes(*args):
		args = [arg.rstrip("/") for arg in args]
		return '/'.join([*args])
	with patch("os.path.join") as mock_method:
		mock_method.side_effect = __join_with_foward_slashes
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_fnmatch_filter():
	with patch("glob.fnmatch.filter") as mock_method:
		mock_method.return_value = []
		yield mock_method

@pytest.fixture
def __mock_glob():
	with patch("glob.glob") as mock_method:
		mock_method.return_value = []
		yield mock_method

@pytest.fixture
def __mock_get_compilation_files():
	with patch(
		"xmipp3_installer.installer.modes.mode_clean.mode_clean_bin_executor.ModeCleanBinExecutor._ModeCleanBinExecutor__get_compilation_files"
	) as mock_method:
		mock_method.return_value = ["compilation_file1", "compilation_file2"]
		yield mock_method

@pytest.fixture
def __mock_get_empty_dirs():
	with patch(
		"xmipp3_installer.installer.modes.mode_clean.mode_clean_bin_executor.ModeCleanBinExecutor._ModeCleanBinExecutor__get_empty_dirs"
	) as mock_method:
		mock_method.return_value = ["empty_dir"]
		yield mock_method

@pytest.fixture
def __mock_get_pycache_dirs():
	with patch(
		"xmipp3_installer.installer.modes.mode_clean.mode_clean_bin_executor.ModeCleanBinExecutor._ModeCleanBinExecutor__get_pycache_dirs"
	) as mock_method:
		mock_method.return_value = ["__pycache__"]
		yield mock_method
