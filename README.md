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
