"""Command line interface for Ultra-Modern Browser."""

import argparse
import os
import sys
import platform
import ctypes
from typing import Optional, List

# Import core components
from ultra_modern_browser import __version__
from ultra_modern_browser.config import load_config
from ultra_modern_browser.logger import setup_logger, get_logger
from ultra_modern_browser.vpn import setup_vpn, cleanup_vpn
from ultra_modern_browser.ui import launch_browser
from ultra_modern_browser.tray import setup_tray_icon

# Setup logger for CLI
logger = get_logger(__name__)


def parse_arguments(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=f"Ultra-Modern Browser with VLESS VPN v{__version__}"
    )
    
    parser.add_argument(
        "--no-vpn", 
        action="store_true", 
        help="Skip VPN (Xray) startup"
    )
    
    parser.add_argument(
        "--config", 
        type=str, 
        help="Path to config file (default: config/config.yaml)"
    )
    
    parser.add_argument(
        "--verbose", "-v", 
        action="count", 
        default=0, 
        help="Increase verbosity (can be used multiple times)"
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version=f"%(prog)s {__version__}"
    )
    
    return parser.parse_args(args)


def setup_windows11_environment():
    """Setup Windows 11 specific environment tweaks."""
    if platform.system() == 'Windows':
        try:
            # Set process as DPI aware
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
            
            # Hide console window
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            if hwnd:
                ctypes.windll.user32.ShowWindow(hwnd, 0)
        except Exception as e:
            logger.warning(f"Failed to setup Windows 11 environment: {e}")


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the application."""
    parsed_args = parse_arguments(args)
    
    # Setup logging based on verbosity
    log_level = max(3 - parsed_args.verbose, 1) * 10  # 10=DEBUG, 20=INFO, 30=WARNING
    setup_logger(level=log_level)
    
    logger.info(f"Starting Ultra-Modern Browser v{__version__}")
    
    try:
        # Setup Windows 11 specific tweaks
        setup_windows11_environment()
        
        # Load configuration
        config = load_config(parsed_args.config)
        
        # Setup tray icon in background thread
        setup_tray_icon()
        
        # Setup VPN if needed
        if not parsed_args.no_vpn:
            setup_vpn(config)
        else:
            logger.info("VPN bypassed by command line argument")
        
        # Launch browser UI with cascading fallback
        launch_browser()
        
        return 0
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
        return 0
    except Exception as e:
        logger.exception(f"Critical error: {e}")
        
        # Show message box on Windows for critical errors
        if platform.system() == 'Windows':
            ctypes.windll.user32.MessageBoxW(
                None, 
                f"Critical error: {e}\n\nCheck logs for details.", 
                "Ultra-Modern Browser Error", 
                0
            )
        return 1
    finally:
        # Always ensure VPN is cleaned up
        cleanup_vpn()


if __name__ == "__main__":
    sys.exit(main())
