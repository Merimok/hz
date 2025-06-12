import os, subprocess, threading, json
import webview


def load_vless_uri():
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


def start_xray():
    try:
        subprocess.Popen([os.path.join('bin', 'xray.exe'), 'run', '-c', 'config/config.json'])
    except FileNotFoundError:
        print('Xray-core не найден в bin/. Положите xray.exe в каталог bin.')


def main():
    uri = load_vless_uri()
    generate_config(uri)
    threading.Thread(target=start_xray, daemon=True).start()
    import ui
    ui.start()


if __name__ == '__main__':
    main()
