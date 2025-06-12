import os
import subprocess
import threading
import json
import urllib.request
import zipfile
import io
import webview


def load_vless_uri():
    env_uri = os.getenv('VLESS_URI')
    if env_uri:
        return env_uri.strip()
    with open(os.path.join('config', 'vless.txt'), 'r') as f:
        return f.read().strip()


def generate_config(uri):
    parts = uri.split('?')
    # Простая генерация JSON на основе vless.txt — допишите парсинг по необходимости
    config = {
        "inbounds": [
            {
                "port": 1080,
                "listen": "127.0.0.1",
                "protocol": "vless",
                "settings": {"clients": [{"id": "331564911"}], "decryption": "none"},
                "streamSettings": {
                    "network": "tcp",
                    "security": "reality",
                    "realitySettings": {
                        "show": False,
                        "fp": "random",
                        "pbk": "EhZf6JqOLErCdliMk1UBlpojo3cfw244QWtoZ-qUFTc",
                        "spx": ["yahoo.com"],
                        "sid": "68c55e5189f67c90"
                    }
                }
            }
        ],
        "outbounds": [{"protocol": "freedom"}]
    }
    with open('config/config.json', 'w') as wf:
        json.dump(config, wf, indent=2)


def ensure_xray():
    xray_path = os.path.join('bin', 'xray.exe')
    if os.path.exists(xray_path):
        return xray_path
    url = 'https://github.com/XTLS/Xray-core/releases/latest/download/Xray-windows-64.zip'
    print('Downloading Xray-core...')
    data = urllib.request.urlopen(url).read()
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        for name in zf.namelist():
            if name.endswith('xray.exe'):
                with open(xray_path, 'wb') as f:
                    f.write(zf.read(name))
                break
    return xray_path


def start_xray():
    ensure_xray()
    try:
        subprocess.Popen([os.path.join('bin', 'xray.exe'), 'run', '-c', 'config/config.json'])
    except FileNotFoundError:
        print('Xray-core не найден и не может быть запущен.')


def main():
    uri = load_vless_uri()
    generate_config(uri)
    os.environ['HTTP_PROXY'] = 'http://127.0.0.1:1080'
    os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:1080'
    threading.Thread(target=start_xray, daemon=True).start()
    import ui
    ui.start()


if __name__ == '__main__':
    main()
