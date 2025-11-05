"""Unit tests for utils/utils.py (0 API calls)."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest
from unittest.mock import patch, MagicMock
from uvisbox_assistant.utils.utils import (
    is_data_tool,
    is_vis_tool,
    get_tool_type,
    cleanup_temp_files,
    get_available_files,
    format_file_list
)


class TestToolTypeDetection:
    """Test tool type detection functions."""

    @patch('uvisbox_assistant.tools.data_tools.DATA_TOOLS', {'generate_curves_ensemble': {}, 'load_csv_to_numpy': {}})
    def test_is_data_tool_returns_true_for_data_tools(self):
        """Test is_data_tool identifies data tools correctly."""
        assert is_data_tool('generate_curves_ensemble') is True
        assert is_data_tool('load_csv_to_numpy') is True

    @patch('uvisbox_assistant.tools.data_tools.DATA_TOOLS', {'generate_curves_ensemble': {}})
    def test_is_data_tool_returns_false_for_non_data_tools(self):
        """Test is_data_tool returns False for non-data tools."""
        assert is_data_tool('plot_functional_boxplot') is False
        assert is_data_tool('unknown_tool') is False

    @patch('uvisbox_assistant.tools.vis_tools.VIS_TOOLS', {'plot_functional_boxplot': {}, 'plot_curve_boxplot': {}})
    def test_is_vis_tool_returns_true_for_vis_tools(self):
        """Test is_vis_tool identifies vis tools correctly."""
        assert is_vis_tool('plot_functional_boxplot') is True
        assert is_vis_tool('plot_curve_boxplot') is True

    @patch('uvisbox_assistant.tools.vis_tools.VIS_TOOLS', {'plot_functional_boxplot': {}})
    def test_is_vis_tool_returns_false_for_non_vis_tools(self):
        """Test is_vis_tool returns False for non-vis tools."""
        assert is_vis_tool('generate_curves_ensemble') is False
        assert is_vis_tool('unknown_tool') is False

    @patch('uvisbox_assistant.tools.data_tools.DATA_TOOLS', {'load_csv': {}})
    @patch('uvisbox_assistant.tools.vis_tools.VIS_TOOLS', {'plot_boxplot': {}})
    @patch('uvisbox_assistant.tools.statistics_tools.STATISTICS_TOOLS', {'compute_stats': {}})
    @patch('uvisbox_assistant.tools.analyzer_tools.ANALYZER_TOOLS', {'generate_report': {}})
    def test_get_tool_type_identifies_all_types(self):
        """Test get_tool_type identifies all tool types."""
        assert get_tool_type('load_csv') == 'data'
        assert get_tool_type('plot_boxplot') == 'vis'
        assert get_tool_type('compute_stats') == 'statistics'
        assert get_tool_type('generate_report') == 'analyzer'
        assert get_tool_type('unknown_tool') == 'unknown'


class TestCleanupTempFiles:
    """Test cleanup_temp_files function."""

    @patch('uvisbox_assistant.utils.utils.config.TEMP_DIR')
    @patch('uvisbox_assistant.utils.utils.config.TEMP_FILE_PREFIX', '_temp_')
    @patch('uvisbox_assistant.utils.utils.config.TEMP_FILE_EXTENSION', '.npy')
    def test_cleanup_when_temp_dir_does_not_exist(self, mock_temp_dir):
        """Test cleanup gracefully handles missing temp directory."""
        mock_temp_dir.exists.return_value = False

        # Should not raise exception
        cleanup_temp_files()

    @patch('uvisbox_assistant.utils.utils.config.TEMP_DIR')
    @patch('uvisbox_assistant.utils.utils.config.TEMP_FILE_PREFIX', '_temp_')
    @patch('uvisbox_assistant.utils.utils.config.TEMP_FILE_EXTENSION', '.npy')
    @patch('builtins.print')
    def test_cleanup_removes_matching_files(self, mock_print, mock_temp_dir):
        """Test cleanup removes files matching pattern."""
        # Setup mock files
        mock_file1 = MagicMock()
        mock_file2 = MagicMock()
        mock_file3 = MagicMock()

        mock_temp_dir.exists.return_value = True
        mock_temp_dir.glob.return_value = [mock_file1, mock_file2, mock_file3]

        cleanup_temp_files()

        # Verify all files were unlinked
        mock_file1.unlink.assert_called_once()
        mock_file2.unlink.assert_called_once()
        mock_file3.unlink.assert_called_once()

        # Verify print was called with count
        mock_print.assert_called_once()
        assert "3" in str(mock_print.call_args)

    @patch('uvisbox_assistant.utils.utils.config.TEMP_DIR')
    @patch('uvisbox_assistant.utils.utils.config.TEMP_FILE_PREFIX', '_temp_')
    @patch('uvisbox_assistant.utils.utils.config.TEMP_FILE_EXTENSION', '.npy')
    @patch('builtins.print')
    def test_cleanup_with_no_files(self, mock_print, mock_temp_dir):
        """Test cleanup with no files to remove."""
        mock_temp_dir.exists.return_value = True
        mock_temp_dir.glob.return_value = []

        cleanup_temp_files()

        # Verify print shows 0 files
        mock_print.assert_called_once()
        assert "0" in str(mock_print.call_args)


class TestGetAvailableFiles:
    """Test get_available_files function."""

    @patch('uvisbox_assistant.utils.utils.config.TEST_DATA_DIR')
    def test_returns_empty_list_when_dir_does_not_exist(self, mock_test_dir):
        """Test returns empty list when directory doesn't exist."""
        mock_test_dir.exists.return_value = False

        result = get_available_files()

        assert result == []

    @patch('uvisbox_assistant.utils.utils.config.TEST_DATA_DIR')
    def test_returns_file_names(self, mock_test_dir):
        """Test returns list of file names."""
        # Setup mock files
        mock_file1 = MagicMock()
        mock_file1.name = 'data1.csv'
        mock_file1.is_file.return_value = True

        mock_file2 = MagicMock()
        mock_file2.name = 'data2.npy'
        mock_file2.is_file.return_value = True

        mock_dir = MagicMock()
        mock_dir.name = 'subdir'
        mock_dir.is_file.return_value = False

        mock_test_dir.exists.return_value = True
        mock_test_dir.iterdir.return_value = [mock_file1, mock_file2, mock_dir]

        result = get_available_files()

        assert result == ['data1.csv', 'data2.npy']

    @patch('uvisbox_assistant.utils.utils.config.TEST_DATA_DIR')
    def test_returns_empty_list_when_no_files(self, mock_test_dir):
        """Test returns empty list when directory has no files."""
        mock_test_dir.exists.return_value = True
        mock_test_dir.iterdir.return_value = []

        result = get_available_files()

        assert result == []


class TestFormatFileList:
    """Test format_file_list function."""

    def test_formats_file_list_correctly(self):
        """Test formatting of file list."""
        files = ['file1.csv', 'file2.npy', 'file3.txt']

        result = format_file_list(files)

        assert '  - file1.csv' in result
        assert '  - file2.npy' in result
        assert '  - file3.txt' in result
        assert result.count('\n') == 2  # 3 files, 2 newlines

    def test_handles_empty_list(self):
        """Test handling of empty file list."""
        result = format_file_list([])

        assert result == "No files available"

    def test_handles_single_file(self):
        """Test formatting single file."""
        result = format_file_list(['single.csv'])

        assert result == '  - single.csv'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
