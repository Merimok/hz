# Lightweight Browser with VLESS VPN


This project provides a minimal Python browser that routes traffic through
**Xray-core** configured with the VLESS protocol.  The repository contains a set
of placeholder files so you can easily replace them with your own settings.

```
project_root/
├─ src/               # Python sources
│   ├─ main.py        # Generates config.json and starts Xray + UI
│   └─ ui.py          # Simple browser interface
├─ config/
│   └─ vless.txt      # Default VLESS URI
├─ resources/
│   └─ bookmarks.json # Sample bookmarks
├─ bin/
│   └─ xray.exe       # Placeholder for Xray-core (Windows)
└─ .github/workflows/build.yml
```

The GitHub Actions workflow builds a Windows executable with PyInstaller and
includes Xray-core. The resulting `lightweight-browser-vless` artifact contains
`main.exe` together with `vless.txt` so the released binary ships with the
sample configuration. You can download the artifact from the workflow run.

## Usage

1. Put a real **xray.exe** into the `bin/` directory (or let the workflow
   download it during CI).
2. Edit `config/vless.txt` if you need a different VLESS URI.
3. Run `python src/main.py` to launch the browser.

`src/main.py` will generate `config/config.json` automatically and start
Xray-core in the background.
=======
This repository contains a minimal Python application that runs a webview-based browser and starts **Xray-core** with a VLESS inbound configuration. The browser routes its traffic through the local VLESS proxy.

The project also includes a GitHub Actions workflow to build a standalone Windows executable using PyInstaller and bundle Xray-core. After PyInstaller finishes, `xray.exe` is copied next to `dist/main.exe` and both binaries are zipped into `release.zip` which is uploaded as the build artifact.

## Usage

1. Provide a VLESS URI via the `VLESS_URI` environment variable or in `vless.txt`.
2. Run `python main.py` to launch the browser with the proxy.

The configuration is generated automatically in `config.json` before starting Xray-core.

