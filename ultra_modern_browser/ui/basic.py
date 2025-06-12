"""Basic UI for Ultra-Modern Browser using PyWebView."""

import os
import sys
import json
from typing import Optional, Dict, Any, List, Callable

from ultra_modern_browser.logger import get_logger

logger = get_logger(__name__)


def start() -> bool:
    """Start the basic browser UI."""
    logger.info("Starting basic UI with PyWebView")
    
    try:
        import webview
        
        # Configure webview settings
        webview.settings.update({
            'ALLOW_DOWNLOADS': True,
            'ALLOW_FILE_ACCESS_FROM_REMOTE': True,
        })
        
        # Create window with basic UI
        window = webview.create_window(
            title='Ultra-Modern Browser',
            url='https://www.google.com',
            js_api=BrowserApi(),
            width=1024,
            height=768
        )
        
        # Start webview
        webview.start(debug=True)
        return True
        
    except ImportError as e:
        logger.error(f"Error starting basic UI: {e}")
        return False
    except Exception as e:
        logger.exception(f"Unexpected error in basic UI: {e}")
        return False


class BrowserApi:
    """JavaScript API for browser integration."""
    
    def __init__(self):
        """Initialize browser API."""
        self.window = None
    
    def init(self, window):
        """Initialize with window reference."""
        self.window = window
    
    def get_vpn_status(self) -> bool:
        """Get VPN connection status."""
        from ultra_modern_browser.vpn import check_vpn_status
        return check_vpn_status()
    
    def toggle_vpn(self) -> bool:
        """Toggle VPN connection status."""
        from ultra_modern_browser.vpn import check_vpn_status, setup_vpn, cleanup_vpn
        
        current_status = check_vpn_status()
        if current_status:
            cleanup_vpn()
            return False
        else:
            from ultra_modern_browser.config import load_config
            return setup_vpn(load_config())
    
    def get_bookmarks(self) -> List[Dict[str, str]]:
        """Get user bookmarks."""
        try:
            with open(os.path.join('resources', 'bookmarks.json'), 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading bookmarks: {e}")
            return [
                {"title": "Google", "url": "https://www.google.com"},
                {"title": "GitHub", "url": "https://github.com"},
                {"title": "Stack Overflow", "url": "https://stackoverflow.com"},
            ]
    
    def save_bookmarks(self, bookmarks: List[Dict[str, str]]) -> bool:
        """Save user bookmarks."""
        try:
            os.makedirs('resources', exist_ok=True)
            with open(os.path.join('resources', 'bookmarks.json'), 'w', encoding='utf-8') as f:
                json.dump(bookmarks, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving bookmarks: {e}")
            return False
    
    def get_app_version(self) -> str:
        """Get application version."""
        from ultra_modern_browser import __version__
        return __version__
