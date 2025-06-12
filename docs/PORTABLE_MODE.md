# Ultra-Modern Browser Portable Mode

## Overview

The portable mode allows you to run Ultra-Modern Browser without installation, making it perfect for:
- Running from USB drives
- Using on restricted systems where you don't have admin rights
- Testing the browser without modifying your system
- Keeping browser settings isolated and containable

## Features

When running in portable mode, Ultra-Modern Browser:

1. Stores all configuration files within the application directory
2. Keeps browser history and bookmarks in the app folder
3. Downloads and stores the Xray binary within the app directory
4. Creates logs in the application's logs folder

## How to Use

### Getting Started

1. Download the portable version: `Ultra-Modern-Browser-v4.0.0-Portable.zip`
2. Extract all contents to any folder of your choice
3. Run `Launch-Browser.bat` to start the application
4. Optionally, create a shortcut to Launch-Browser.bat on your desktop

### Configuration

In portable mode, the configuration is stored in:
- `config/config.yaml` - Main configuration file
- `config/bookmarks.json` - Browser bookmarks
- `portable.txt` - Special file that marks portable mode (do not delete)

### Using VLESS URI

To use a VLESS URI in portable mode:

1. Create a `vless.txt` file in the application folder
2. Paste your VLESS URI into this file
3. Restart the application

## Technical Details

### How Portable Mode Works

The application detects portable mode by:
1. Checking for the existence of a `portable.txt` file in the same directory as the executable
2. Adjusting all file paths to be relative to the application directory instead of system locations
3. Creating a self-contained environment for configuration and data

### Folder Structure

A typical portable installation includes:

```
Ultra-Modern-Browser-Portable/
├── app/                  # Application files
│   ├── ultra-browser.exe # Main executable
│   └── ... (app files)   # App support files  
├── bin/                  # Binary files
│   └── xray.exe          # Xray VPN binary
├── config/               # Configuration
│   └── config.yaml       # Main config
├── logs/                 # Log files
├── portable.txt          # Portable mode marker
└── Launch-Browser.bat    # Startup script
```

## Limitations

Some features have limited functionality in portable mode:

1. Automatic updates are disabled
2. System integration features (like auto-start) are not available
3. System-wide proxy settings cannot be modified

## Troubleshooting

If the application doesn't start in portable mode:

1. Make sure `portable.txt` exists in the application directory
2. Check that the `app` folder contains all required files
3. Verify that `Launch-Browser.bat` points to the correct executable
4. Check the logs folder for any error messages
