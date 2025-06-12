"""System tray icon implementation for Ultra-Modern Browser."""

import os
import sys
import threading
from typing import Optional, Callable

from ultra_modern_browser.logger import get_logger

logger = get_logger(__name__)

# Global reference to tray icon
_tray_icon = None


def setup_tray_icon() -> bool:
    """Setup and display the system tray icon."""
    try:
        import pystray
        from PIL import Image, ImageDraw
        
        logger.info("Setting up system tray icon")
        
        # Create icon image
        icon_image = _create_tray_image()
        
        # Build menu
        menu = pystray.Menu(
            pystray.MenuItem("Open Browser", _on_open_browser),
            pystray.MenuItem("Enable VPN", _on_toggle_vpn, checked=lambda _: _get_vpn_status()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("About", _on_about),
            pystray.MenuItem("Exit", _on_quit)
        )
        
        # Create and start tray icon in background thread
        global _tray_icon
        _tray_icon = pystray.Icon(
            'UltraModernBrowser',
            icon_image,
            'Ultra-Modern Browser',
            menu
        )
        
        threading.Thread(target=lambda: _tray_icon.run(), daemon=True).start()
        logger.info("Tray icon started")
        return True
        
    except ImportError:
        logger.warning("Pystray or PIL not available, tray icon disabled")
        return False
    except Exception as e:
        logger.error(f"Error setting up tray icon: {e}")
        return False


def _create_tray_image():
    """Create the tray icon image."""
    from PIL import Image, ImageDraw
    
    width = 64
    height = 64
    
    # Check if custom icon exists
    icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'icon.png')
    if os.path.exists(icon_path):
        try:
            return Image.open(icon_path)
        except Exception as e:
            logger.warning(f"Failed to load custom icon: {e}")
    
    # Create a simple icon (black and white)
    image = Image.new('RGB', (width, height), (0, 0, 0))
    dc = ImageDraw.Draw(image)
    
    # Draw a browser-like symbol (upper half)
    dc.rectangle((width//4, height//4, 3*width//4, 3*height//4), fill=(50, 120, 220))
    dc.rectangle((width//4, height//4, 3*width//4, height//3), fill=(30, 90, 180))
    
    # Draw VPN-like symbol (lower half)
    dc.arc((width//4, height//2, 3*width//4, 3*height//4), 
           start=0, end=180, fill=(255, 255, 255), width=3)
    
    return image


def _on_open_browser(icon, item):
    """Open the browser window if minimized or not running."""
    logger.info("Tray: Open browser requested")
    # In a real implementation, this would connect to any minimized window
    # or launch a new instance if needed


def _on_toggle_vpn(icon, item):
    """Toggle VPN on/off."""
    from ultra_modern_browser.vpn import setup_vpn, cleanup_vpn
    
    if _get_vpn_status():
        logger.info("Tray: VPN disable requested")
        cleanup_vpn()
    else:
        logger.info("Tray: VPN enable requested")
        from ultra_modern_browser.config import load_config
        setup_vpn(load_config())


def _on_about(icon, item):
    """Show about dialog."""
    import ctypes
    from ultra_modern_browser import __version__
    
    logger.info("Tray: About dialog requested")
    ctypes.windll.user32.MessageBoxW(
        None, 
        f"Ultra-Modern Browser v{__version__}\n\n"
        "A modern web browser with integrated VLESS VPN\n"
        "For Windows 11",
        "About Ultra-Modern Browser", 
        0
    )


def _on_quit(icon, item):
    """Exit the application."""
    logger.info("Tray: Exit requested")
    
    # Cleanup VPN if running
    from ultra_modern_browser.vpn import cleanup_vpn
    cleanup_vpn()
    
    # Stop the icon
    icon.stop()
    
    # Exit the application
    sys.exit(0)


def _get_vpn_status() -> bool:
    """Check if VPN is active."""
    from ultra_modern_browser.vpn import check_vpn_status
    return check_vpn_status()
