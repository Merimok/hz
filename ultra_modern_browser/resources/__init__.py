"""Ultra-Modern Browser resource module."""

import os
import importlib.resources

def get_resource_path(path: str) -> str:
    """Get path to a resource file."""
    package = "ultra_modern_browser.resources"
    
    try:
        # Python 3.10+ way
        return str(importlib.resources.files(package).joinpath(path))
    except (AttributeError, ImportError):
        # Python 3.8+ fallback
        return os.path.join(os.path.dirname(__file__), "resources", path)
