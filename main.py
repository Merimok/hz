import os
import subprocess
import threading
import webview
import json
import urllib.request
import zipfile
import io
from urllib.parse import urlparse, parse_qs


def get_vless_uri():
    """Загружает VLESS URI из переменной окружения или файла vless.txt."""
    uri = os.getenv('VLESS_URI')
    if not uri:
        try:
            with open('vless.txt', 'r', encoding='utf-8') as f:
                uri = f.readline().strip()
        except FileNotFoundError:
            try:
                with open(os.path.join('config', 'vless.txt'), 'r', encoding='utf-8') as f:
                    uri = f.readline().strip()
            except FileNotFoundError:
                print("VLESS URI не найден. Проверьте файл vless.txt или переменную VLESS_URI")
                uri = ''
    return uri


def generate_config(uri: str):
    """Генерирует конфигурацию config.json на основе VLESS URI."""
    # Default values from sample
    cfg = {
        'id': '331564911',
        'fp': 'random',
        'pbk': 'EhZf6JqOLErCdliMk1UBlpojo3cfw244QWtoZ-qUFTc',
        'spx': ['yahoo.com'],
        'sid': '68c55e5189f67c90'
    }
    
    # Парсинг VLESS URI
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
        if 'sni' in qs:
            cfg['spx'] = [qs['sni'][0]]
        if 'sid' in qs:
            cfg['sid'] = qs['sid'][0]
    except Exception as e:
        print(f"Ошибка парсинга VLESS URI: {e}")
        print("Используются значения по умолчанию")

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
    print("Конфигурация config.json успешно создана")


def ensure_xray():
    """Проверяет наличие xray.exe и загружает его при необходимости."""
    xray_path = os.path.join('bin', 'xray.exe')
    
    # Создаём папку bin если её нет
    os.makedirs('bin', exist_ok=True)
    
    if os.path.exists(xray_path):
        print(f"Xray найден: {xray_path}")
        return xray_path
    
    print("Xray не найден. Загрузка из GitHub...")
    url = 'https://github.com/XTLS/Xray-core/releases/latest/download/Xray-windows-64.zip'
    
    try:
        print('Загрузка Xray-core...')
        data = urllib.request.urlopen(url).read()
        
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            for name in zf.namelist():
                if name.endswith('xray.exe'):
                    with open(xray_path, 'wb') as f:
                        f.write(zf.read(name))
                    print(f"Xray успешно загружен: {xray_path}")
                    return xray_path
                    
        print("xray.exe не найден в архиве")
        return None
        
    except Exception as e:
        print(f"Ошибка загрузки Xray: {e}")
        return None


def start_xray():
    """Запускает Xray-core с загрузкой бинарника при необходимости."""
    xray_path = ensure_xray()
    if not xray_path:
        print("Не удалось получить Xray-core. Продолжение без VPN.")
        return
    
    try:
        print(f"Запуск Xray: {xray_path}")
        process = subprocess.Popen([xray_path, 'run', '-c', 'config.json'])
        print(f"Xray запущен с PID: {process.pid}")
    except FileNotFoundError:
        print('Xray исполняемый файл не найден.')
    except Exception as e:
        print(f'Ошибка запуска Xray: {e}')


def main():
    """Главная функция приложения."""
    print("=== Лёгкий браузер с VLESS VPN ===")
    
    # Загрузка и проверка VLESS URI
    uri = get_vless_uri()
    if not uri:
        print("Предупреждение: VLESS URI не настроен")
    
    # Генерация конфигурации
    generate_config(uri)

    # Настройка прокси
    os.environ['HTTP_PROXY'] = 'http://127.0.0.1:1080'
    os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:1080'

    # Запуск Xray в фоновом режиме
    threading.Thread(target=start_xray, daemon=True).start()
    
    # Небольшая задержка для запуска Xray
    import time
    time.sleep(2)
    
    # Запуск браузера
    print("Запуск браузера...")
    webview.create_window('Lightweight Browser with VLESS VPN', 'https://www.google.com')
    webview.start()


if __name__ == '__main__':
    main()
