"""Configuration management module for Ultra-Modern Browser."""

import os
import sys
import yaml
import json
import jsonschema
from pathlib import Path
from typing import Dict, Any, Optional

from ultra_modern_browser.logger import get_logger

logger = get_logger(__name__)

# Flag for portable mode
PORTABLE_MODE = False

# Default config values
DEFAULT_CONFIG = {
    "vpn": {
        "id": "331564911",
        "address": "94.131.110.172",
        "port": 23209,
        "fp": "random",
        "pbk": "EhZf6JqOLErCdliMk1UBlpojo3cfw244QWtoZ-qUFTc",
        "sni": "yahoo.com", 
        "sid": "68c55e5189f67c90"
    },
    "browser": {
        "title": "Ultra-Modern Browser v4.0.0",
        "width": 1024,
        "height": 768,
        "ui_themes": ["modern", "dark", "light"],
        "default_home": "https://www.google.com"
    },
    "logging": {
        "level": "INFO",
        "max_files": 5,
        "max_size_mb": 5
    }
}

# Check if we're in portable mode
def _init_portable_mode():
    global PORTABLE_MODE
    try:
        exe_path = os.path.abspath(sys.executable)
        exe_dir = os.path.dirname(exe_path)
        if os.path.exists(os.path.join(exe_dir, 'portable.txt')):
            PORTABLE_MODE = True
            logger.info(f"Running in portable mode from {exe_dir}")
    except Exception as e:
        logger.debug(f"Failed to check for portable mode: {e}")

# Initialize on module load
_init_portable_mode()

# JSON Schema for Xray configuration validation
XRAY_CONFIG_SCHEMA = {
    "type": "object",
    "required": ["log", "inbounds", "outbounds"],
    "properties": {
        "log": {
            "type": "object",
            "properties": {
                "loglevel": {"type": "string"}
            }
        },
        "inbounds": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["port", "listen", "protocol"],
                "properties": {
                    "port": {"type": "integer"},
                    "listen": {"type": "string"},
                    "protocol": {"type": "string"}
                }
            }
        },
        "outbounds": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["protocol", "settings"],
                "properties": {
                    "protocol": {"type": "string"},
                    "settings": {"type": "object"}
                }
            }
        }
    }
}


def get_config_path(config_path: Optional[str] = None) -> str:
    """Determine the configuration file path."""
    if config_path:
        return config_path
    
    # Prepare possible config locations
    locations = []
    
    # Add portable mode paths first if applicable
    global PORTABLE_MODE
    if PORTABLE_MODE:
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        locations.extend([
            os.path.join(exe_dir, 'config', 'config.yaml'),
            os.path.join(exe_dir, 'config.yaml'),
        ])
    
    # Add standard paths
    locations.extend([
        'config/config.yaml',
        os.path.expanduser('~/ultra_modern_browser/config.yaml'),
        os.path.join(os.path.dirname(__file__), 'config/config.yaml')
    ])
    
    # Return first existing config path
    for path in locations:
        if os.path.exists(path):
            return path
    
    # If no config files exist, default to creating in portable location or current directory
    if PORTABLE_MODE:
        return os.path.join(os.path.dirname(os.path.abspath(sys.executable)), 'config', 'config.yaml')
    else:
        return 'config/config.yaml'


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from YAML file with fallback to defaults."""
    config = DEFAULT_CONFIG.copy()
    
    try:
        config_file = get_config_path(config_path)
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                loaded_config = yaml.safe_load(f)
                if loaded_config:
                    # Deep merge configs
                    _deep_update(config, loaded_config)
            logger.info(f"Configuration loaded from {config_file}")
        else:
            logger.warning(f"Configuration file not found: {config_file}, using defaults")
            
            # Create default config if it doesn't exist
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.safe_dump(config, f, default_flow_style=False)
            logger.info(f"Default configuration created at {config_file}")
            
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
    
    # Load VLESS URI and merge into config
    vless_uri = get_vless_uri()
    if vless_uri:
        vpn_config = parse_vless_uri(vless_uri)
        if vpn_config:
            config['vpn'].update(vpn_config)
    
    return config


def get_vless_uri() -> str:
    """Get VLESS URI from environment or file."""
    uri = os.getenv('VLESS_URI', '')
    
    if not uri:
        # Try loading from vless.txt in different locations
        for path in ['vless.txt', 'config/vless.txt']:
            try:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        uri = f.readline().strip()
                    logger.info(f"VLESS URI loaded from {path}")
                    break
            except Exception as e:
                logger.error(f"Error reading {path}: {e}")
    
    if uri:
        logger.info(f"VLESS URI loaded (length: {len(uri)})")
    else:
        logger.warning("VLESS URI not found")
        
    return uri


def parse_vless_uri(uri: str) -> Dict[str, Any]:
    """Parse VLESS URI into configuration dictionary."""
    import urllib.parse as urlparse
    
    vpn_config = {}
    
    if not uri.startswith('vless://'):
        logger.warning("Invalid VLESS URI format")
        return vpn_config
    
    try:
        parsed = urlparse.urlparse(uri)
        
        # Extract user ID (username)
        if parsed.username:
            vpn_config['id'] = parsed.username
        
        # Extract address and port
        if parsed.hostname:
            vpn_config['address'] = parsed.hostname
        
        if parsed.port:
            vpn_config['port'] = parsed.port
        
        # Parse query parameters
        qs = urlparse.parse_qs(parsed.query)
        for key in ['fp', 'pbk', 'sni', 'sid']:
            if key in qs:
                vpn_config[key] = qs[key][0]
        
    except Exception as e:
        logger.error(f"Error parsing VLESS URI: {e}")
    
    return vpn_config


def generate_xray_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate Xray configuration from app config."""
    vpn = config.get('vpn', {})
    
    xray_config = {
        "log": {
            "loglevel": "info"
        },
        "inbounds": [
            {
                "port": 1080,
                "listen": "127.0.0.1",
                "protocol": "socks",
                "sniffing": {
                    "enabled": True,
                    "destOverride": ["http", "tls"]
                },
                "settings": {
                    "auth": "noauth",
                    "udp": True
                }
            }
        ],
        "outbounds": [
            {
                "protocol": "vless",
                "settings": {
                    "vnext": [
                        {
                            "address": vpn.get('address'),
                            "port": vpn.get('port'),
                            "users": [
                                {
                                    "id": vpn.get('id'),
                                    "encryption": "none"
                                }
                            ]
                        }
                    ]
                },
                "streamSettings": {
                    "network": "tcp",
                    "security": "reality",
                    "realitySettings": {
                        "show": False,
                        "fingerprint": vpn.get('fp'),
                        "serverName": vpn.get('sni'),
                        "publicKey": vpn.get('pbk'),
                        "shortId": vpn.get('sid')
                    }
                }
            }
        ]
    }
    
    # Validate the configuration against schema
    try:
        jsonschema.validate(instance=xray_config, schema=XRAY_CONFIG_SCHEMA)
        logger.info("Xray configuration validated successfully")
    except jsonschema.exceptions.ValidationError as e:
        logger.error(f"Xray configuration validation error: {e}")
    
    # Save the config to file
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(xray_config, f, ensure_ascii=False, indent=2)
    
    return xray_config


def _deep_update(d: Dict[str, Any], u: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively update nested dictionaries."""
    for k, v in u.items():
        if isinstance(v, dict) and isinstance(d.get(k), dict):
            d[k] = _deep_update(d[k], v)
        else:
            d[k] = v
    return d
