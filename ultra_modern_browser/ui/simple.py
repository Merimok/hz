"""Simple UI for Ultra-Modern Browser (Tkinter fallback)."""

import os
import sys
import webbrowser
import threading
from typing import Optional, Dict, Any

from ultra_modern_browser.logger import get_logger

logger = get_logger(__name__)


def start() -> bool:
    """Start the simple browser UI using Tkinter."""
    logger.info("Starting simple UI with Tkinter")
    
    try:
        # Import tkinter here to avoid dependency for other UIs
        import tkinter as tk
        from tkinter import ttk, messagebox
        
        # Root window
        root = tk.Tk()
        root.title("Ultra-Modern Browser (Simple UI)")
        root.geometry("800x600")
        
        # Configure grid
        root.columnconfigure(0, weight=1)
        root.rowconfigure(1, weight=1)
        
        # Navigation frame
        nav_frame = ttk.Frame(root)
        nav_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # URL entry
        url_var = tk.StringVar(value="https://www.google.com")
        ttk.Label(nav_frame, text="URL:").pack(side=tk.LEFT, padx=(0, 5))
        url_entry = ttk.Entry(nav_frame, width=70, textvariable=url_var)
        url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Navigation buttons
        ttk.Button(nav_frame, text="Go", command=lambda: _open_url(url_var.get())).pack(side=tk.LEFT)
        
        # Status frame
        status_frame = ttk.Frame(root)
        status_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=(0, 5))
        
        # Status label
        status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=status_var)
        status_label.pack(side=tk.LEFT)
        
        # Content frame (for displaying info)
        content_frame = ttk.Frame(root, relief=tk.SUNKEN, borderwidth=1)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Content text area
        content_text = tk.Text(content_frame, wrap=tk.WORD)
        content_text.pack(fill=tk.BOTH, expand=True)
        content_text.insert(tk.END, 
            "Ultra-Modern Browser (Simple UI)\n\n"
            "This is the simple fallback UI when PyWebView is not available.\n"
            "Enter a URL above and click 'Go' to open it in your default browser.\n\n"
            "For the full experience, please ensure PyWebView is installed:\n"
            "pip install pywebview>=3.6\n\n"
            "Status: VPN is running in the background (if enabled)."
        )
        
        # Function to open URL
        def _open_url(url: str) -> None:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            status_var.set(f"Opening: {url}")
            root.update_idletasks()
            
            try:
                webbrowser.open(url)
                status_var.set(f"Opened: {url}")
            except Exception as e:
                status_var.set(f"Error: {e}")
        
        # Handle window close
        def _on_close():
            from ultra_modern_browser.vpn import cleanup_vpn
            cleanup_vpn()
            root.destroy()
            
        root.protocol("WM_DELETE_WINDOW", _on_close)
        
        # Start Tkinter main loop
        root.mainloop()
        return True
        
    except ImportError as e:
        logger.error(f"Error starting simple UI: {e}")
        return False
    except Exception as e:
        logger.exception(f"Unexpected error in simple UI: {e}")
        return False
