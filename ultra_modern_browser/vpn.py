"""VPN service module for Ultra-Modern Browser."""

import os
import sys
import subprocess
import time
import zipfile
import io
import urllib.request
import platform
from pathlib import Path
from typing import Optional, Dict, Any

from ultra_modern_browser.logger import get_logger

logger = get_logger(__name__)

# Global reference to Xray process
_xray_process: Optional[subprocess.Popen] = None


def setup_vpn(config: Dict[str, Any]) -> bool:
    """Set up and start the VPN service."""
    logger.info("Setting up VPN service")
    
    # Generate Xray configuration
    from ultra_modern_browser.config import generate_xray_config
    xray_config = generate_xray_config(config)
    
    # Setup proxy environment variables
    os.environ['HTTP_PROXY'] = 'socks5://127.0.0.1:1080'
    os.environ['HTTPS_PROXY'] = 'socks5://127.0.0.1:1080'
    
    # Start Xray process
    xray_path = ensure_xray_binary()
    if not xray_path:
        logger.error("Failed to find or download Xray binary")
        return False
    
    # Start Xray with retry
    if start_xray(xray_path):
        logger.info("VPN service started successfully")
        return True
    
    return False


def cleanup_vpn() -> None:
    """Clean up VPN resources and terminate Xray."""
    global _xray_process
    
    if _xray_process:
        logger.info(f"Terminating Xray process (PID: {_xray_process.pid})")
        try:
            _xray_process.terminate()
            _xray_process.wait(timeout=3)
            _xray_process = None
        except Exception as e:
            logger.error(f"Error terminating Xray process: {e}")
            
            # Force kill if termination failed
            try:
                if _xray_process and _xray_process.poll() is None:
                    _xray_process.kill()
            except:
                pass


def ensure_xray_binary() -> Optional[str]:
    """Ensure Xray binary exists, downloading if necessary."""
    # Determine binary name based on platform
    xray_binary = "xray.exe" if platform.system() == "Windows" else "xray"
    
    # Check for portable mode
    portable_mode = False
    try:
        from ultra_modern_browser.config import PORTABLE_MODE
        portable_mode = PORTABLE_MODE
    except ImportError:
        pass
    
    # List possible paths where xray binary might be located
    possible_paths = []
    
    # Add portable mode paths first if applicable
    if portable_mode:
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        possible_paths.extend([
            os.path.join(exe_dir, 'bin', xray_binary),
            os.path.join(exe_dir, xray_binary),
        ])
    
    # Add standard paths
    possible_paths.extend([
        os.path.join('bin', xray_binary),
        os.path.join(os.getcwd(), 'bin', xray_binary),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'bin', xray_binary)
    ])
    
    # Check if binary already exists in any of the paths
    for path in possible_paths:
        if os.path.exists(path):
            logger.info(f"Xray binary found at: {path}")
            return path
            
    # Determine the target directory for download
    if portable_mode:
        bin_dir = os.path.join(os.path.dirname(os.path.abspath(sys.executable)), 'bin')
    else:
        bin_dir = 'bin'
        
    # Create bin directory if it doesn't exist
    os.makedirs(bin_dir, exist_ok=True)
    
    # Target path for the downloaded binary
    xray_path = os.path.join(bin_dir, xray_binary)
    
    # Download from GitHub if not found
    logger.info("Xray binary not found, downloading from GitHub...")
    url = 'https://github.com/XTLS/Xray-core/releases/latest/download/Xray-windows-64.zip'
    
    try:
        # Create a progress bar for the download
        def _report_progress(block_count, block_size, total_size):
            downloaded = block_count * block_size
            percent = min(100, int(downloaded * 100 / total_size))
            sys.stdout.write(f"\rDownloading Xray: {percent}% [{downloaded}/{total_size} bytes]")
            sys.stdout.flush()
        
        # Download the file
        logger.info(f"Downloading Xray from: {url}")
        filename, _ = urllib.request.urlretrieve(url, reporthook=_report_progress)
        print()  # Newline after progress
        
        # Extract xray.exe from the zip
        with zipfile.ZipFile(filename) as zf:
            for name in zf.namelist():
                if name.endswith('xray.exe'):
                    with open(xray_path, 'wb') as f:
                        f.write(zf.read(name))
                    logger.info(f"Xray successfully extracted to: {xray_path}")
                    return xray_path
        
        logger.error("xray.exe not found in the downloaded archive")
        return None
    
    except Exception as e:
        logger.error(f"Error downloading Xray: {e}")
        return None
    finally:
        # Clean up temporary files
        if 'filename' in locals():
            try:
                os.unlink(filename)
            except:
                pass


def start_xray(xray_path: str, retries: int = 3) -> bool:
    """Start Xray process with retry mechanism."""
    global _xray_process
    
    for attempt in range(1, retries + 1):
        try:
            logger.info(f"Starting Xray (attempt {attempt}/{retries}): {xray_path}")
            
            # Start Xray process
            _xray_process = subprocess.Popen(
                [xray_path, 'run', '-c', 'config.json'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW  # Windows-specific: hide console
            )
            
            # Wait a moment to ensure it started properly
            time.sleep(1)
            
            # Check if process is still running
            if _xray_process.poll() is None:
                logger.info(f"Xray started with PID: {_xray_process.pid}")
                return True
            else:
                # Process exited immediately - get error output
                stdout, stderr = _xray_process.communicate()
                logger.error(f"Xray failed to start: {stderr.decode('utf-8', errors='ignore')}")
                _xray_process = None
        
        except Exception as e:
            logger.error(f"Error starting Xray (attempt {attempt}): {e}")
        
        # Wait before retry
        if attempt < retries:
            time.sleep(attempt)  # Progressive delay
    
    logger.critical("Failed to start Xray after multiple attempts")
    return False


def check_vpn_status() -> bool:
    """Check if VPN is active and working."""
    global _xray_process
    
    if not _xray_process:
        return False
    
    # Check if process is still running
    if _xray_process.poll() is not None:
        logger.error(f"Xray process terminated unexpectedly, return code: {_xray_process.returncode}")
        _xray_process = None
        return False
    
    # TODO: Add connectivity test to check if VPN is actually working
    
    return True
