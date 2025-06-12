# Lightweight Browser with VLESS VPN

This repository contains a minimal Python application that runs a webview-based browser and starts **Xray-core** with a VLESS inbound configuration. The browser routes its traffic through the local VLESS proxy.

The project also includes a GitHub Actions workflow to build a standalone Windows executable using PyInstaller and bundle Xray-core.

After a successful run, the executable can be downloaded from the workflow as the
`lightweight-browser-vless` artifact.

## Usage

1. Provide a VLESS URI via the `VLESS_URI` environment variable or in `vless.txt`.
2. Run `python main.py` to launch the browser with the proxy.

The configuration is generated automatically in `config.json` before starting Xray-core.
