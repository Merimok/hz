"""
Build script for portable version of Ultra-Modern Browser.
This creates a standalone executable with all dependencies.
"""

import os
import sys
import shutil
import platform
from pathlib import Path
import PyInstaller.__main__

def build_portable():
    """Build portable version of Ultra-Modern Browser."""
    print("Building portable version of Ultra-Modern Browser...")
    
    # Base directory
    base_dir = Path(__file__).resolve().parent
    dist_dir = base_dir / "dist"
    build_dir = base_dir / "build"
    portable_dir = dist_dir / "Ultra-Modern-Browser-Portable"
    
    # Clean previous build
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)
        
    # Create required directories
    os.makedirs(portable_dir / "config", exist_ok=True)
    os.makedirs(portable_dir / "bin", exist_ok=True)
    os.makedirs(portable_dir / "logs", exist_ok=True)
    
    # Files to include in the portable package
    include_files = [
        ("config/config.yaml", "config/"),
        ("README.md", ""),
    ]
    
    # PyInstaller command arguments
    pyinstaller_args = [
        "--noconfirm",
        "--clean",
        "--name=ultra-browser",
        "--icon=ultra_modern_browser/resources/browser.ico",
        "--add-data=ultra_modern_browser/resources;ultra_modern_browser/resources",
        "--hidden-import=webview.platforms.cef",
        "--hidden-import=ultra_modern_browser.ui.basic",
        "--hidden-import=ultra_modern_browser.ui.simple",
        "--hidden-import=ultra_modern_browser.ui",
        "--hidden-import=PIL._tkinter_finder",
        "--onedir",
        "--noconsole",
        "ultra_modern_browser/cli.py",
    ]
    
    # Add Windows specific options
    if platform.system() == "Windows":
        pyinstaller_args.append("--uac-admin")  # Request admin rights for proper VPN setup
    
    # Run PyInstaller
    PyInstaller.__main__.run(pyinstaller_args)
    
    # Copy the PyInstaller build to our portable directory
    pyinst_dir = dist_dir / "ultra-browser"
    
    # Copy the PyInstaller files
    for item in pyinst_dir.iterdir():
        if item.is_dir():
            shutil.copytree(item, portable_dir / item.name)
        else:
            shutil.copy2(item, portable_dir)
    
    # Copy additional files
    for src, dst_dir in include_files:
        src_path = base_dir / src
        if src_path.exists():
            dst_path = portable_dir / dst_dir
            if not dst_path.exists():
                dst_path.mkdir(parents=True, exist_ok=True)
            if src_path.is_dir():
                shutil.copytree(src_path, dst_path / src_path.name)
            else:
                shutil.copy2(src_path, dst_path / src_path.name)
    
    # Create launcher batch file
    with open(portable_dir / "Ultra-Modern-Browser.bat", "w") as f:
        f.write('@echo off\n')
        f.write('cd /d "%~dp0"\n')
        f.write('start "" "ultra-browser.exe"\n')
    
    # Create a "Portable Mode" marker file
    with open(portable_dir / "portable.txt", "w") as f:
        f.write("Ultra-Modern Browser Portable Mode\n")
        f.write("Do not delete this file\n")
    
    # Create a zip archive of the portable directory
    shutil.make_archive(str(dist_dir / "Ultra-Modern-Browser-Portable-Win11"), "zip", dist_dir, "Ultra-Modern-Browser-Portable")
    
    print(f"Portable version created at: {portable_dir}")
    print(f"Zip archive created at: {dist_dir}/Ultra-Modern-Browser-Portable-Win11.zip")
    return True

if __name__ == "__main__":
    build_portable()
