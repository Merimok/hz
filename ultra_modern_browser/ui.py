"""UI module for Ultra-Modern Browser."""

import importlib
from typing import List, Optional

from ultra_modern_browser.logger import get_logger, log_exception

logger = get_logger(__name__)

# UI modules with fallback priority
UI_MODULES = [
    'ultra_modern_browser.ui.modern_ultra',
    'ultra_modern_browser.ui.modern_fixed',
    'ultra_modern_browser.ui.modern',
    'ultra_modern_browser.ui.basic',
    'ultra_modern_browser.ui.simple',
]


def launch_browser() -> bool:
    """Launch browser UI with cascading fallback mechanism."""
    logger.info("Launching Ultra-Modern Browser UI...")
    
    for module_name in UI_MODULES:
        try:
            logger.info(f"Trying UI module: {module_name}")
            module = importlib.import_module(module_name)
            
            # Each UI module must expose a start() function
            if hasattr(module, 'start'):
                success = module.start()
                if success:
                    logger.info(f"Successfully launched UI: {module_name}")
                    return True
                else:
                    logger.warning(f"UI module {module_name} started but returned failure")
            else:
                logger.error(f"UI module {module_name} missing start() function")
        
        except ImportError as e:
            logger.warning(f"UI module {module_name} not available: {e}")
        except Exception as e:
            log_exception(logger, e, f"UI module {module_name}")
    
    logger.critical("All UI modules failed to launch")
    return False
