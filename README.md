# Lightweight Browser with VLESS VPN

This repository contains a minimal Python application that runs a webview-based browser and starts **Xray-core** with a VLESS inbound configuration. The browser routes its traffic through the local VLESS proxy.

The project also includes a GitHub Actions workflow to build a standalone Windows executable using PyInstaller and bundle Xray-core.

## Project tree

```
.
├── .github/
│   └── workflows/
│       └── build.yml
├── README.md
├── config.json
├── main.py
└── vless.txt
```

## Usage

1. Set the `VLESS_URI` environment variable or put the URI in `vless.txt`.
   The variable is optional – if not provided, the first line of `vless.txt` is used.
2. Run `python main.py` to launch the browser with the proxy.

The configuration is generated automatically in `config.json` before starting Xray-core.
The executable produced by the GitHub Actions workflow can be downloaded from the
**Actions** tab on GitHub by selecting a workflow run and fetching the
`lightweight-browser-vless` artifact.
