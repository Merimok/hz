"""Tests for the CLI module."""

import unittest
from unittest.mock import patch, MagicMock
import sys
import io
import platform

from ultra_modern_browser.cli import parse_arguments, setup_windows11_environment, main


class TestCLI(unittest.TestCase):
    """Test cases for Command Line Interface."""

    def test_parse_arguments_defaults(self):
        """Test parsing arguments with default values."""
        # Test with no args
        with patch('sys.argv', ['ultra-browser']):
            args = parse_arguments([])
            self.assertFalse(args.no_vpn)
            self.assertIsNone(args.config)
            self.assertEqual(args.verbose, 0)
    
    def test_parse_arguments_custom(self):
        """Test parsing arguments with custom values."""
        args = parse_arguments(['--no-vpn', '--config', 'test.yaml', '-vv'])
        self.assertTrue(args.no_vpn)
        self.assertEqual(args.config, 'test.yaml')
        self.assertEqual(args.verbose, 2)
    
    @patch('platform.system')
    @patch('ctypes.windll.shcore.SetProcessDpiAwareness')
    @patch('ctypes.windll.kernel32.GetConsoleWindow')
    @patch('ctypes.windll.user32.ShowWindow')
    def test_setup_windows11_environment(self, mock_show_window, mock_get_console, 
                                        mock_set_dpi, mock_platform):
        """Test Windows 11 environment setup."""
        # Test on Windows
        mock_platform.return_value = 'Windows'
        mock_get_console.return_value = 123  # Mock window handle
        
        setup_windows11_environment()
        
        mock_set_dpi.assert_called_once_with(1)
        mock_get_console.assert_called_once()
        mock_show_window.assert_called_once_with(123, 0)
        
        # Test on non-Windows
        mock_platform.return_value = 'Linux'
        mock_set_dpi.reset_mock()
        mock_get_console.reset_mock()
        mock_show_window.reset_mock()
        
        setup_windows11_environment()
        
        mock_set_dpi.assert_not_called()
        mock_get_console.assert_not_called()
        mock_show_window.assert_not_called()
    
    @patch('ultra_modern_browser.cli.parse_arguments')
    @patch('ultra_modern_browser.cli.setup_logger')
    @patch('ultra_modern_browser.cli.load_config')
    @patch('ultra_modern_browser.cli.setup_tray_icon')
    @patch('ultra_modern_browser.cli.setup_vpn')
    @patch('ultra_modern_browser.cli.launch_browser')
    @patch('ultra_modern_browser.cli.cleanup_vpn')
    def test_main_successful(self, mock_cleanup, mock_launch, mock_setup_vpn, 
                            mock_tray, mock_config, mock_logger, mock_parse_args):
        """Test successful execution flow."""
        # Setup mocks
        args = MagicMock()
        args.no_vpn = False
        args.config = None
        args.verbose = 1
        mock_parse_args.return_value = args
        mock_config.return_value = {'test': 'config'}
        mock_launch.return_value = True
        
        # Call function
        result = main(['--verbose'])
        
        # Verify
        self.assertEqual(result, 0)
        mock_setup_vpn.assert_called_once()
        mock_launch.assert_called_once()
        mock_cleanup.assert_called_once()
    
    @patch('ultra_modern_browser.cli.parse_arguments')
    @patch('ultra_modern_browser.cli.setup_logger')
    @patch('ultra_modern_browser.cli.cleanup_vpn')
    @patch('platform.system')
    @patch('ctypes.windll.user32.MessageBoxW')
    def test_main_exception(self, mock_msgbox, mock_platform, mock_cleanup, 
                          mock_logger, mock_parse_args):
        """Test exception handling in main."""
        # Setup mocks
        mock_parse_args.side_effect = Exception("Test error")
        mock_platform.return_value = 'Windows'
        
        # Call function
        result = main([])
        
        # Verify
        self.assertEqual(result, 1)
        mock_cleanup.assert_called_once()
        mock_msgbox.assert_called_once()


if __name__ == '__main__':
    unittest.main()
