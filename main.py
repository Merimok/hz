import os
import subprocess
import threading
import webview
import json
from urllib.parse import urlparse, parse_qs


def get_vless_uri():
    uri = os.getenv('VLESS_URI')
    if not uri:
        try:
            with open('vless.txt', 'r', encoding='utf-8') as f:
                uri = f.readline().strip()
        except FileNotFoundError:
            uri = ''
    return uri


def generate_config(uri: str):
    # Default values from sample
    cfg = {
        'id': '331564911',
        'fp': 'random',
        'pbk': 'EhZf6JqOLErCdliMk1UBlpojo3cfw244QWtoZ-qUFTc',
        'spx': ['yahoo.com'],
        'sid': '68c55e5189f67c90'
    }
    try:
        parsed = urlparse(uri)
        if parsed.username:
            cfg['id'] = parsed.username
        qs = parse_qs(parsed.query)
        if 'fp' in qs:
            cfg['fp'] = qs['fp'][0]
        if 'pbk' in qs:
            cfg['pbk'] = qs['pbk'][0]
        if 'spx' in qs:
            cfg['spx'] = [qs['spx'][0]]
        if 'sid' in qs:
            cfg['sid'] = qs['sid'][0]
    except Exception:
        pass

    config = {
        'inbounds': [
            {
                'port': 1080,
                'listen': '127.0.0.1',
                'protocol': 'vless',
                'settings': {
                    'clients': [
                        {'id': cfg['id']}
                    ],
                    'decryption': 'none'
                },
                'streamSettings': {
                    'network': 'tcp',
                    'security': 'reality',
                    'realitySettings': {
                        'show': False,
                        'fp': cfg['fp'],
                        'pbk': cfg['pbk'],
                        'spx': cfg['spx'],
                        'sid': cfg['sid']
                    }
                }
            }
        ],
        'outbounds': [{'protocol': 'freedom'}]
    }
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def start_xray():
    try:
        subprocess.Popen(['xray', 'run', '-c', 'config.json'])
    except FileNotFoundError:
        print('Xray executable not found.')


def main():
    uri = get_vless_uri()
    generate_config(uri)

    os.environ['HTTP_PROXY'] = 'http://127.0.0.1:1080'
    os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:1080'

    threading.Thread(target=start_xray, daemon=True).start()
    webview.create_window('Lightweight Browser with VLESS VPN', 'https://example.com')
    webview.start()


if __name__ == '__main__':
    main()
