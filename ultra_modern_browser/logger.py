"""Logger configuration for Ultra-Modern Browser."""

import os
import sys
import logging
import traceback
import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict


# Global logger registry
_loggers: Dict[str, logging.Logger] = {}


def get_logger(name: str) -> logging.Logger:
    """Get or create a logger by name."""
    if name in _loggers:
        return _loggers[name]
    
    logger = logging.getLogger(name)
    _loggers[name] = logger
    return logger


def setup_logger(
    level: int = logging.INFO,
    log_dir: str = 'logs',
    max_size_mb: int = 5,
    backup_count: int = 5
) -> logging.Logger:
    """Configure the root logger with console and file handlers."""
    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Generate log filename with timestamp
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'browser_{timestamp}.log')
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers if any
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler with custom formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    ))
    console_handler.setLevel(level)
    root_logger.addHandler(console_handler)
    
    # Create rotating file handler
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_size_mb * 1024 * 1024,  # Convert MB to bytes
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    root_logger.addHandler(file_handler)
    
    # Register the main browser logger
    browser_logger = get_logger('ultra_modern_browser')
    browser_logger.info(f"Logging initialized, level={logging.getLevelName(level)}")
    browser_logger.info(f"Log file: {log_file}")
    
    return browser_logger


def log_exception(logger: logging.Logger, exception: Exception, context: str = "") -> None:
    """Log an exception with detailed traceback."""
    exc_info = sys.exc_info()
    tb_lines = traceback.format_exception(*exc_info)
    tb_text = ''.join(tb_lines)
    
    context_msg = f" in {context}" if context else ""
    logger.error(f"Exception{context_msg}: {exception}")
    logger.debug(f"Traceback:\n{tb_text}")
    
    # Add error report to sentry if available
    try:
        import sentry_sdk
        if sentry_sdk.Hub.current.client:
            sentry_sdk.capture_exception(exception)
    except (ImportError, Exception):
        pass  # Sentry not available or error occurred


def init_sentry(dsn: Optional[str] = None) -> bool:
    """Initialize Sentry error reporting if available."""
    if not dsn:
        return False
    
    try:
        import sentry_sdk
        from ultra_modern_browser import __version__
        
        sentry_sdk.init(
            dsn=dsn,
            release=f"ultra_modern_browser@{__version__}",
            environment="production",
            traces_sample_rate=0.1,
        )
        return True
    except ImportError:
        get_logger(__name__).warning(
            "Sentry SDK not installed. Install with pip install ultra_modern_browser[monitoring]"
        )
        return False
    except Exception as e:
        get_logger(__name__).error(f"Failed to initialize Sentry: {e}")
        return False


# Create convenience alias for browser_logger
browser_logger = get_logger('ultra_modern_browser')
