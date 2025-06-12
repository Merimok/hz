"""Tests for the VPN module."""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import shutil
import json

from ultra_modern_browser.vpn import setup_vpn, cleanup_vpn, check_vpn_status, ensure_xray_binary


class TestVPN(unittest.TestCase):
    """Test cases for VPN module."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
        
    def tearDown(self):
        """Clean up after tests."""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
    
    @patch('subprocess.Popen')
    @patch('ultra_modern_browser.vpn.ensure_xray_binary')
    @patch('ultra_modern_browser.config.generate_xray_config')
    def test_setup_vpn_success(self, mock_generate_config, mock_ensure_xray, mock_popen):
        """Test VPN setup with successful execution."""
        # Mock configuration
        mock_config = {
            'vpn': {
                'id': 'test-id',
                'address': '127.0.0.1',
                'port': 1234
            }
        }
        
        # Mock xray config generation
        mock_generate_config.return_value = {
            'log': {'loglevel': 'info'},
            'inbounds': [{'port': 1080, 'listen': '127.0.0.1', 'protocol': 'socks'}],
            'outbounds': [{'protocol': 'vless', 'settings': {}}]
        }
        
        # Mock xray binary path
        mock_ensure_xray.return_value = os.path.join(self.test_dir, 'bin', 'xray.exe')
        
        # Mock subprocess.Popen
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Process is running
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        # Call function
        result = setup_vpn(mock_config)
        
        # Verify
        self.assertTrue(result)
        mock_generate_config.assert_called_once_with(mock_config)
        mock_ensure_xray.assert_called_once()
        mock_popen.assert_called_once()
        
        # Check if environment variables are set
        self.assertEqual(os.environ.get('HTTP_PROXY'), 'socks5://127.0.0.1:1080')
        self.assertEqual(os.environ.get('HTTPS_PROXY'), 'socks5://127.0.0.1:1080')
    
    @patch('ultra_modern_browser.vpn.ensure_xray_binary')
    def test_setup_vpn_missing_binary(self, mock_ensure_xray):
        """Test VPN setup with missing Xray binary."""
        # Mock missing xray binary
        mock_ensure_xray.return_value = None
        
        # Call function
        result = setup_vpn({'vpn': {}})
        
        # Verify
        self.assertFalse(result)
    
    @patch('ultra_modern_browser.vpn._xray_process')
    def test_check_vpn_status_active(self, mock_process):
        """Test VPN status check when VPN is active."""
        # Mock running process
        mock_process.poll.return_value = None  # Process is running
        
        # Call function
        result = check_vpn_status()
        
        # Verify
        self.assertTrue(result)
    
    @patch('ultra_modern_browser.vpn._xray_process', None)
    def test_check_vpn_status_inactive(self):
        """Test VPN status check when VPN is not running."""
        # Call function
        result = check_vpn_status()
        
        # Verify
        self.assertFalse(result)
    
    @patch('os.path.exists')
    @patch('ultra_modern_browser.vpn.urllib.request')
    @patch('zipfile.ZipFile')
    @patch('builtins.open', new_callable=mock_open)
    def test_ensure_xray_binary_download(self, mock_file, mock_zipfile, mock_request, mock_exists):
        """Test downloading Xray binary when it doesn't exist."""
        # Mock file checks
        mock_exists.return_value = False
        
        # Mock urllib.request
        mock_request.urlretrieve = MagicMock(return_value=('temp_file', None))
        
        # Mock zipfile
        mock_zip_instance = MagicMock()
        mock_zip_instance.namelist.return_value = ['xray.exe']
        mock_zip_instance.read.return_value = b'binary_data'
        mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
        
        # Call function
        result = ensure_xray_binary()
        
        # Verify
        self.assertIsNotNone(result)
        mock_file.assert_called()
        mock_zip_instance.read.assert_called_once_with('xray.exe')


if __name__ == '__main__':
    unittest.main()
