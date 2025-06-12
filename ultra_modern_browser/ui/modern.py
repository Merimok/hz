"""Modern UI for Ultra-Modern Browser using PyWebView with advanced features."""

import os
import json
import webview
import threading
from typing import Optional, Dict, Any, List, Callable
from pathlib import Path

from ultra_modern_browser.logger import get_logger
from ultra_modern_browser.config import load_config

logger = get_logger(__name__)

# Global window reference
_window: Optional[webview.Window] = None

# Path to HTML resources
RESOURCES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'resources')


def load_html_template(theme: str = 'modern') -> str:
    """Load HTML template with specified theme."""
    try:
        theme_file = f"{theme.lower()}.html"
        theme_path = os.path.join(RESOURCES_PATH, theme_file)
        
        # Check if theme exists or use default
        if not os.path.exists(theme_path):
            logger.warning(f"Theme {theme} not found, using default")
            theme_path = os.path.join(RESOURCES_PATH, "modern.html")
        
        # Read the template
        with open(theme_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        return html_content
    except Exception as e:
        logger.error(f"Error loading HTML template: {e}")
        return """<!DOCTYPE html>
        <html><head><title>Error</title></head>
        <body><h1>Error Loading Template</h1></body></html>"""


class BrowserApi:
    """JavaScript API for the browser."""
    
    def __init__(self, window: webview.Window):
        self.window = window
        self.config = load_config()
    
    def load_url(self, url: str) -> bool:
        """Load a URL in the browser."""
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        
        try:
            self.window.load_url(url)
            return True
        except Exception as e:
            logger.error(f"Error loading URL {url}: {e}")
            return False
    
    def get_history(self) -> List[str]:
        """Get browser history."""
        # This would be implemented with local storage
        return []
    
    def add_bookmark(self, url: str, title: str) -> bool:
        """Add a bookmark."""
        try:
            # Implementation would save to a bookmarks file
            return True
        except Exception as e:
            logger.error(f"Error adding bookmark: {e}")
            return False


def start() -> bool:
    """Start the modern browser UI."""
    logger.info("Starting modern UI with PyWebView")
    
    try:
        # Initialize browser API and config
        config = load_config()
        
        # Configure webview settings for Windows 11
        if hasattr(webview.settings, 'update'):
            webview.settings.update({
                'ALLOW_DOWNLOADS': True,
                'ALLOW_FILE_ACCESS_FROM_REMOTE': True,
                'OPEN_EXTERNAL_LINKS_IN_BROWSER': True,
                'USER_AGENT': config.get('browser', {}).get(
                    'user_agent', 
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
                )
            })
        
        # Get window config
        width = config.get('browser', {}).get('width', 1280)
        height = config.get('browser', {}).get('height', 800)
        title = config.get('browser', {}).get('title', 'Ultra-Modern Browser v4.0.0')
        default_url = config.get('browser', {}).get('default_home', 'https://www.google.com')
        theme = config.get('browser', {}).get('theme', 'modern')
        
        # Create the window with modern UI
        global _window
        _window = webview.create_window(
            title=title,
            url=default_url,
            width=width,
            height=height,
            min_size=(800, 600),
            background_color='#2e2e2e',
            frameless=False,
        )
        
        # Create and attach JS API
        _window.expose(BrowserApi(_window))
        
        # Start webview in current thread
        webview.start(debug=False, gui='cef')
        
        return True
        
    except ImportError as e:
        logger.error(f"Modern UI dependencies not available: {e}")
        return False
    except Exception as e:
        logger.error(f"Error starting modern UI: {e}")
        return False


def cleanup() -> None:
    """Clean up resources."""
    global _window
    if _window:
        try:
            _window.destroy()
        except:
            pass
        _window = None


if __name__ == "__main__":
    start()
