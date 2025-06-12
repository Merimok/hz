# 🌐 Ultra-Modern Browser with VLESS VPN v4.0.0

![Status](https://img.shields.io/badge/Status-Production%20Ready-green)
![Version](https://img.shields.io/badge/Version-v4.0.0-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%2011-lightgrey)

Ultra-Modern Browser with integrated VLESS VPN support via Xray-core. Optimized specifically for Windows 11 with modern UI and automatic VPN configuration.

## ✨ Features

- 🔐 **VLESS + Reality VPN** - Secure connection through Xray-core
- 🎨 **Windows 11 Native UI** - Modern interface with Windows 11 optimizations
- 🖼️ **System Integration** - System tray icon, DPI awareness, and native dialogs
- 🔄 **UI Fallback System** - 5 levels of cascading UI modules
- ⚡ **Auto-Configuration** - Automatic Xray download and setup
- 🌍 **Full Navigation** - Complete browser functionality with address bar and navigation buttons
- 🔖 **Bookmarks System** - Quick access to favorite websites
- 🔄 **Tab Management** - Open, close, and switch between tabs easily
- 🛡️ **Enhanced Error Handling** - Comprehensive error management
- 📦 **Portable Mode** - Run without installation, perfect for USB drives

## 📋 System Requirements

- Windows 11 (21H2 or later) 64-bit
- 4GB RAM
- 500MB free disk space
- Internet connection for VPN functionality

## 🚀 Quick Start

### Portable Version (No Installation Required)
1. Download `Ultra-Modern-Browser-v4.0.0-Portable.zip` from [Releases](../../releases)
2. Extract all contents to any folder of your choice
3. Run `Launch-Browser.bat` to start the application

### From Source Code
1. Clone the repository
2. Install dependencies with `pip install -e .`
3. Run the browser: `python -m ultra_modern_browser.cli`

## 🔧 Configuration

Configuration is stored in `config/config.yaml`. You can customize:

- VPN settings (address, port, encryption parameters)
- Browser UI preferences
- Logging levels and rotation settings

## 💡 Using VLESS URI

You can provide a VLESS URI in three ways:
1. Environment variable: `VLESS_URI=vless://...`
2. Create `vless.txt` in the application directory
3. Create `config/vless.txt` with your VLESS URI

## 🔧 Development

### Requirements

- Python 3.8 or higher
- Development dependencies: `pip install -e .[dev]`

### Running Tests

```bash
pytest tests/
```

### Building Portable Version

```bash
python build_portable.py
```

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🛠️ Technical Overview

- **Modular Architecture:** Component-based design with clear separations
- **Dynamic UI Loading:** Cascading UI module system with fallbacks
- **Configuration Management:** YAML-based with schema validation
- **Windows 11 Integration:** DPI awareness, system tray, native dialogs
- **Enhanced Logging:** Rotation-based logging with proper levels
- **Portable Mode:** Self-contained application with runtime detection

## 📊 Additional Resources

- [API Documentation](docs/API.md)
- [VPN Configuration Guide](docs/VPN.md)
- [Building from Source](docs/BUILD.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
