"""Tests for the configuration module."""

import os
import tempfile
import unittest
from unittest.mock import patch, mock_open

from ultra_modern_browser.config import load_config, generate_xray_config


class TestConfig(unittest.TestCase):
    """Test cases for configuration module."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_yaml = """
vpn:
  id: "test-id"
  address: "127.0.0.1"
  port: 1234
  fp: "test-fp"
  pbk: "test-pbk"
  sni: "example.com"
  sid: "test-sid"
browser:
  title: "Test Browser"
  width: 800
  height: 600
  theme: "test"
"""

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('yaml.safe_load')
    def test_load_config_custom_path(self, mock_yaml_load, mock_file, mock_exists):
        """Test loading configuration from a custom path."""
        # Setup mocks
        mock_exists.return_value = True
        mock_yaml_load.return_value = {
            'vpn': {'id': 'test-id'},
            'browser': {'title': 'Test Browser'}
        }
        
        # Call function
        config = load_config('custom_path.yaml')
        
        # Verify
        self.assertEqual(config['vpn']['id'], 'test-id')
        self.assertEqual(config['browser']['title'], 'Test Browser')
        mock_file.assert_called_once_with('custom_path.yaml', 'r', encoding='utf-8')

    @patch('os.path.exists')
    def test_load_config_default(self, mock_exists):
        """Test loading default configuration when file doesn't exist."""
        # Setup mocks
        mock_exists.return_value = False
        
        # Call function
        config = load_config()
        
        # Verify default values
        self.assertIn('vpn', config)
        self.assertIn('browser', config)
        self.assertIn('logging', config)

    def test_generate_xray_config(self):
        """Test generating Xray configuration from app config."""
        # Setup test config
        config = {
            'vpn': {
                'id': 'test-id',
                'address': '127.0.0.1',
                'port': 1234,
                'fp': 'test-fp',
                'pbk': 'test-pbk',
                'sni': 'example.com',
                'sid': 'test-sid'
            }
        }
        
        # Call function
        with patch('ultra_modern_browser.config.validate_xray_config', return_value=True):
            xray_config = generate_xray_config(config)
        
        # Verify parts of the Xray config
        self.assertEqual(xray_config['log']['loglevel'], 'info')
        self.assertEqual(xray_config['inbounds'][0]['port'], 1080)
        self.assertEqual(xray_config['outbounds'][0]['protocol'], 'vless')


if __name__ == '__main__':
    unittest.main()
