"""Ultra Modern UI for Windows 11 with advanced features and custom styling."""

import os
import json
import webview
import threading
import platform
from typing import Optional, Dict, Any, List, Callable
from pathlib import Path

from ultra_modern_browser.logger import get_logger, log_exception
from ultra_modern_browser.config import load_config
from ultra_modern_browser.vpn import check_vpn_status

logger = get_logger(__name__)

# Global window reference
_window: Optional[webview.Window] = None

# Path to HTML resources
RESOURCES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'resources')


class UltraModernAPI:
    """Advanced JavaScript API for Ultra Modern Browser."""
    
    def __init__(self, window: webview.Window):
        self.window = window
        self.config = load_config()
        self.history = []
        self.bookmarks = []
        # Load saved bookmarks if available
        self._load_bookmarks()
        
    def navigate(self, url: str) -> bool:
        """Navigate to URL with validation and logging."""
        try:
            if not url.startswith(('http://', 'https://')):
                url = f"https://{url}"
            
            # Add to history
            if url not in self.history:
                self.history.append(url)
                # Keep history at reasonable size
                if len(self.history) > 100:
                    self.history = self.history[-100:]
            
            # Load the URL
            self.window.load_url(url)
            return True
        except Exception as e:
            log_exception(logger, e, f"Error navigating to {url}")
            return False
    
    def check_connection(self) -> Dict[str, Any]:
        """Check connection status including VPN."""
        try:
            vpn_status = check_vpn_status()
            return {
                'vpn': vpn_status,
                'internet': True  # We would implement a real check here
            }
        except Exception as e:
            log_exception(logger, e, "Error checking connection")
            return {'vpn': False, 'internet': False, 'error': str(e)}
    
    def add_bookmark(self, url: str, title: str) -> bool:
        """Add a bookmark with error handling."""
        try:
            if not url.startswith(('http://', 'https://')):
                url = f"https://{url}"
            
            # Add to bookmarks if not already there
            bookmark = {'url': url, 'title': title or url}
            if bookmark not in self.bookmarks:
                self.bookmarks.append(bookmark)
                self._save_bookmarks()
                
            return True
        except Exception as e:
            log_exception(logger, e, f"Error adding bookmark for {url}")
            return False
    
    def get_bookmarks(self) -> List[Dict[str, str]]:
        """Get all bookmarks."""
        return self.bookmarks
    
    def get_history(self) -> List[str]:
        """Get browsing history."""
        return self.history
    
    def clear_history(self) -> bool:
        """Clear browsing history."""
        try:
            self.history = []
            return True
        except Exception as e:
            log_exception(logger, e, "Error clearing history")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        try:
            return {
                'os': platform.system(),
                'os_version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'python': platform.python_version(),
                'app_version': '4.0.0'
            }
        except Exception as e:
            log_exception(logger, e, "Error getting system info")
            return {'error': str(e)}
    
    def _save_bookmarks(self) -> None:
        """Save bookmarks to JSON file."""
        try:
            # Determine bookmarks path based on portable mode
            from ultra_modern_browser.config import PORTABLE_MODE
            
            if PORTABLE_MODE:
                # In portable mode, save relative to executable
                exe_dir = os.path.dirname(os.path.abspath(sys.executable))
                bookmarks_path = os.path.join(exe_dir, 'config', 'bookmarks.json')
            else:
                # In normal mode, save in config directory
                bookmarks_path = 'config/bookmarks.json'
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(bookmarks_path), exist_ok=True)
            
            # Save bookmarks
            with open(bookmarks_path, 'w', encoding='utf-8') as f:
                json.dump(self.bookmarks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log_exception(logger, e, "Error saving bookmarks")
            
    def _load_bookmarks(self) -> None:
        """Load bookmarks from JSON file."""
        try:
            # Try both portable and standard paths
            paths = ['config/bookmarks.json']
            
            # Add portable path if applicable
            try:
                from ultra_modern_browser.config import PORTABLE_MODE
                if PORTABLE_MODE:
                    exe_dir = os.path.dirname(os.path.abspath(sys.executable))
                    paths.insert(0, os.path.join(exe_dir, 'config', 'bookmarks.json'))
            except:
                pass
            
            # Try each path
            for path in paths:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        self.bookmarks = json.load(f)
                    logger.info(f"Loaded {len(self.bookmarks)} bookmarks from {path}")
                    return
        except Exception as e:
            log_exception(logger, e, "Error loading bookmarks")
            self.bookmarks = []


def load_html_template() -> str:
    """Load HTML template for the browser UI."""
    try:
        # Try to find the ultra modern template
        template_path = os.path.join(RESOURCES_PATH, 'ultra_modern.html')
        if not os.path.exists(template_path):
            # Fall back to standard resources
            logger.warning("Ultra modern template not found, using built-in template")
            return """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ultra Modern Browser</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #202020;
            color: #fff;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            height: 100vh;
        }
        .toolbar {
            display: flex;
            padding: 10px;
            background-color: #2d2d2d;
            border-bottom: 1px solid #444;
            align-items: center;
        }
        .nav-buttons {
            display: flex;
            margin-right: 10px;
        }
        .nav-btn {
            background-color: transparent;
            border: none;
            color: #fff;
            font-size: 18px;
            cursor: pointer;
            margin: 0 5px;
            padding: 5px 10px;
            border-radius: 4px;
        }
        .nav-btn:hover {
            background-color: #444;
        }
        .url-bar {
            flex: 1;
            padding: 8px 10px;
            border-radius: 20px;
            border: 1px solid #555;
            background-color: #333;
            color: #fff;
            outline: none;
            font-size: 14px;
        }
        .url-bar:focus {
            border-color: #0078d7;
        }
        .browser-frame {
            flex: 1;
            border: none;
            width: 100%;
            height: 100%;
        }
        .menu-btn {
            background-color: transparent;
            border: none;
            color: #fff;
            font-size: 18px;
            cursor: pointer;
            margin-left: 10px;
            padding: 5px 10px;
            border-radius: 4px;
        }
        .menu-btn:hover {
            background-color: #444;
        }
        .connection-status {
            margin-left: 10px;
            font-size: 12px;
            display: flex;
            align-items: center;
        }
        .status-indicator {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }
        .status-connected {
            background-color: #4CAF50;
        }
        .status-disconnected {
            background-color: #F44336;
        }
    </style>
</head>
<body>
    <div class="toolbar">
        <div class="nav-buttons">
            <button class="nav-btn" onclick="history.back()">&#8592;</button>
            <button class="nav-btn" onclick="history.forward()">&#8594;</button>
            <button class="nav-btn" onclick="location.reload()">&#8635;</button>
        </div>
        <input type="text" class="url-bar" id="urlBar" placeholder="Search or enter website name"
               onkeypress="if(event.keyCode===13)navigateToUrl()">
        <div class="connection-status">
            <div id="statusIndicator" class="status-indicator"></div>
            <span id="statusText">Checking...</span>
        </div>
        <button class="menu-btn" onclick="toggleMenu()">&#8942;</button>
    </div>
    <iframe id="browserFrame" class="browser-frame" src="about:blank"></iframe>

    <script>
        // Initialize UI
        document.addEventListener('DOMContentLoaded', function() {
            // Set initial URL
            document.getElementById('browserFrame').src = "https://www.google.com";
            
            // Check connection status
            checkConnection();
            setInterval(checkConnection, 10000); // Check every 10 seconds
            
            // Update URL bar when iframe loads
            document.getElementById('browserFrame').addEventListener('load', function() {
                document.getElementById('urlBar').value = this.contentWindow.location.href;
            });
        });
        
        function navigateToUrl() {
            var url = document.getElementById('urlBar').value.trim();
            if (url) {
                window.pywebview.api.navigate(url);
            }
        }
        
        function toggleMenu() {
            // Menu would be implemented here
            alert('Menu coming soon!');
        }
        
        function checkConnection() {
            window.pywebview.api.check_connection().then(function(status) {
                var indicator = document.getElementById('statusIndicator');
                var statusText = document.getElementById('statusText');
                
                if (status.vpn) {
                    indicator.className = 'status-indicator status-connected';
                    statusText.textContent = 'VPN Connected';
                } else {
                    indicator.className = 'status-indicator status-disconnected';
                    statusText.textContent = 'VPN Disconnected';
                }
            });
        }
    </script>
</body>
</html>
"""
        
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error loading HTML template: {e}")
        # Return a simple template in case of error
        return """<!DOCTYPE html>
<html><head><title>Error</title></head>
<body><h1>Error Loading Template</h1><p>Please check logs for details.</p></body></html>"""


def start() -> bool:
    """Start the ultra modern browser UI."""
    logger.info("Starting ultra modern UI")
    
    try:
        # Check if we're on Windows 11
        is_windows11 = False
        if platform.system() == 'Windows':
            try:
                import sys
                if sys.getwindowsversion().build >= 22000:  # Windows 11 build number
                    is_windows11 = True
            except:
                pass
        
        if not is_windows11:
            logger.warning("Ultra Modern UI is optimized for Windows 11, falling back to regular Modern UI")
            # We could import and call the modern.py module here
            return False
        
        # Initialize config
        config = load_config()
        browser_config = config.get('browser', {})
        
        # Configure webview settings
        if hasattr(webview.settings, 'update'):
            webview.settings.update({
                'ALLOW_DOWNLOADS': True,
                'OPEN_EXTERNAL_LINKS_IN_BROWSER': True,
                'USER_AGENT': browser_config.get(
                    'user_agent', 
                    'Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
                )
            })
        
        # Get window config
        width = browser_config.get('width', 1280)
        height = browser_config.get('height', 800)
        title = browser_config.get('title', 'Ultra-Modern Browser v4.0.0')
        
        # Load HTML template
        html_content = load_html_template()
        
        # Create window
        global _window
        _window = webview.create_window(
            title=title,
            html=html_content,
            js_api=UltraModernAPI(_window),
            width=width,
            height=height,
            min_size=(800, 600),
            background_color='#202020',
            frameless=False,
        )
        
        # Start webview
        webview.start(debug=False)
        
        return True
    except ImportError as e:
        logger.error(f"Ultra Modern UI dependencies not available: {e}")
        return False
    except Exception as e:
        log_exception(logger, e, "Error starting Ultra Modern UI")
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
