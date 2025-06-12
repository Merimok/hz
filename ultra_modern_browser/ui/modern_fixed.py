"""Modern Fixed UI for Ultra-Modern Browser using PyWebView with stability enhancements."""

import os
import webview
import threading
from typing import Optional, Dict, Any, List, Callable

from ultra_modern_browser.logger import get_logger, log_exception
from ultra_modern_browser.config import load_config
from ultra_modern_browser.ui import modern  # Import regular modern UI as fallback

logger = get_logger(__name__)

# Global window reference
_window: Optional[webview.Window] = None


def start() -> bool:
    """Start the modern fixed browser UI with additional stability."""
    logger.info("Starting modern fixed UI with PyWebView")
    
    try:
        # Initialize browser API and config
        config = load_config()
        
        # Get window config
        width = config.get('browser', {}).get('width', 1024)
        height = config.get('browser', {}).get('height', 768)
        title = config.get('browser', {}).get('title', 'Ultra-Modern Browser v4.0.0')
        default_url = config.get('browser', {}).get('default_home', 'https://www.google.com')
        
        # Configure webview with additional safeguards
        try:
            if hasattr(webview.settings, 'update'):
                webview.settings.update({
                    'ALLOW_DOWNLOADS': True,
                    'ALLOW_FILE_ACCESS_FROM_REMOTE': False,  # More secure setting
                    'OPEN_EXTERNAL_LINKS_IN_BROWSER': True,  # Safer for external links
                    'TEXT_SELECT': True,
                    'ZOOMABLE': True,
                    'USER_AGENT': config.get('browser', {}).get(
                        'user_agent', 
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
                    )
                })
        except Exception as e:
            logger.warning(f"Failed to update webview settings: {e}")
        
        # Create window with error handling
        global _window
        try:
            # First try direct URL mode which is more stable for some backends
            _window = webview.create_window(
                title=title,
                url=default_url,
                width=width,
                height=height,
                min_size=(800, 600),
                background_color='#FFFFFF',
                frameless=False,
                easy_drag=True,
                js_api=BrowserApi(),
            )
        except Exception as e:
            logger.warning(f"Failed to create window with URL: {e}, trying HTML mode")
            
            # Fall back to HTML mode
            html_content = """<!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta http-equiv="refresh" content="0;url={}">
                <script>
                    window.location.href = "{}";
                </script>
            </head>
            <body>
                <p>Redirecting to {}</p>
            </body>
            </html>""".format(default_url, default_url, default_url)
            
            _window = webview.create_window(
                title=title,
                html=html_content,
                width=width,
                height=height,
                min_size=(800, 600),
                js_api=BrowserApi(),
            )
            
        # Start webview with proper error handling
        try:
            webview.start(debug=False, gui='cef')
            return True
        except Exception as e:
            logger.error(f"Failed to start webview with CEF: {e}")
            try:
                # Try alternative GUI toolkit
                if _window:
                    _window.destroy()
                webview.start(debug=False, gui='qt')
                return True
            except Exception as e2:
                logger.error(f"Failed to start webview with Qt: {e2}")
                # Fall back to default/system GUI toolkit as last resort
                try:
                    if _window:
                        _window.destroy()
                    webview.start(debug=False)
                    return True
                except Exception as e3:
                    logger.error(f"Failed to start webview with default GUI: {e3}")
                    # Fall back to regular modern UI
                    return modern.start()
                
    except ImportError as e:
        logger.error(f"Modern Fixed UI dependencies not available: {e}")
        # Try falling back to regular modern UI
        return modern.start()
    except Exception as e:
        log_exception(logger, e, "Error starting modern fixed UI")
        # Try falling back to regular modern UI
        return modern.start()


class BrowserApi:
    """JavaScript API for the browser with enhanced error handling."""
    
    def __init__(self):
        self.config = load_config()
    
    def load_url(self, url: str) -> bool:
        """Load a URL with proper error handling."""
        global _window
        if not _window:
            return False
            
        try:
            if not url.startswith(('http://', 'https://')):
                url = f"https://{url}"
                
            _window.load_url(url)
            return True
        except Exception as e:
            log_exception(logger, e, f"Error loading URL: {url}")
            try:
                # Try HTML-based navigation as fallback
                html_content = f"""<!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <meta http-equiv="refresh" content="0;url={url}">
                    <script>
                        window.location.href = "{url}";
                    </script>
                </head>
                <body>
                    <p>Redirecting to {url}</p>
                </body>
                </html>"""
                _window.load_html(html_content)
                return True
            except Exception as e2:
                log_exception(logger, e2, "Error with HTML fallback")
                return False
    
    def check_connection(self) -> Dict[str, Any]:
        """Check VPN and internet connection."""
        from ultra_modern_browser.vpn import check_vpn_status
        
        try:
            vpn_active = check_vpn_status()
            return {
                'vpn': vpn_active,
                'internet': True  # We'd implement a real check here
            }
        except Exception as e:
            log_exception(logger, e, "Error checking connection")
            return {'vpn': False, 'internet': False}


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
