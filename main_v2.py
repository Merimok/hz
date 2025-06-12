import os
import subprocess
import threading
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
    # Default values
    cfg = {
        'id': '331564911',
        'address': '94.131.110.172',
        'port': 23209,
        'fp': 'random',
        'pbk': 'EhZf6JqOLErCdliMk1UBlpojo3cfw244QWtoZ-qUFTc',
        'sni': 'yahoo.com',
        'sid': '68c55e5189f67c90'
    }
    
    # Парсинг VLESS URI
    if uri and uri.startswith('vless://'):
        try:
            parsed = urlparse(uri)
            print(f"Парсинг URI: {uri}")
            
            # Извлекаем ID (username)
            if parsed.username:
                cfg['id'] = parsed.username
                print(f"ID: {cfg['id']}")
            
            # Извлекаем адрес и порт
            if parsed.hostname:
                cfg['address'] = parsed.hostname
                print(f"Адрес: {cfg['address']}")
            
            if parsed.port:
                cfg['port'] = parsed.port
                print(f"Порт: {cfg['port']}")
            
            # Парсим параметры запроса
            qs = parse_qs(parsed.query)
            if 'fp' in qs:
                cfg['fp'] = qs['fp'][0]
                print(f"Fingerprint: {cfg['fp']}")
            if 'pbk' in qs:
                cfg['pbk'] = qs['pbk'][0]
                print(f"Public Key: {cfg['pbk'][:20]}...")
            if 'sni' in qs:
                cfg['sni'] = qs['sni'][0]
                print(f"SNI: {cfg['sni']}")
            if 'sid' in qs:
                cfg['sid'] = qs['sid'][0]
                print(f"Short ID: {cfg['sid']}")
                
        except Exception as e:
            print(f"Ошибка парсинга VLESS URI: {e}")
            print("Используются значения по умолчанию")
    else:
        print("VLESS URI не найден, используются значения по умолчанию")

    # Генерация правильной конфигурации для Xray-core
    config = {
        'log': {
            'loglevel': 'info'
        },
        'inbounds': [
            {
                'port': 1080,
                'listen': '127.0.0.1',
                'protocol': 'socks',
                'sniffing': {
                    'enabled': True,
                    'destOverride': ['http', 'tls']
                },
                'settings': {
                    'auth': 'noauth',
                    'udp': True
                }
            }
        ],
        'outbounds': [
            {
                'protocol': 'vless',
                'settings': {
                    'vnext': [
                        {
                            'address': cfg['address'],
                            'port': cfg['port'],
                            'users': [
                                {
                                    'id': cfg['id'],
                                    'encryption': 'none'
                                }
                            ]
                        }
                    ]
                },
                'streamSettings': {
                    'network': 'tcp',
                    'security': 'reality',
                    'realitySettings': {
                        'show': False,
                        'fingerprint': cfg['fp'],
                        'serverName': cfg['sni'],
                        'publicKey': cfg['pbk'],
                        'shortId': cfg['sid']
                    }
                }
            }
        ]
    }
    
    print(f"Создание конфигурации для сервера {cfg['address']}:{cfg['port']}")
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
        return process
    except FileNotFoundError:
        print('Xray исполняемый файл не найден.')
    except Exception as e:
        print(f'Ошибка запуска Xray: {e}')
    return None


def main():
    """Главная функция приложения."""
    print("=== Лёгкий браузер с VLESS VPN v2.0 ===")
    
    # Загрузка и проверка VLESS URI
    uri = get_vless_uri()
    if not uri:
        print("Предупреждение: VLESS URI не настроен")
    
    # Генерация конфигурации
    generate_config(uri)

    # Настройка прокси для SOCKS
    os.environ['HTTP_PROXY'] = 'socks5://127.0.0.1:1080'
    os.environ['HTTPS_PROXY'] = 'socks5://127.0.0.1:1080'

    # Запуск Xray в фоновом режиме
    print("Запуск VPN сервиса...")
    threading.Thread(target=start_xray, daemon=True).start()
    
    # Небольшая задержка для запуска Xray
    import time
    time.sleep(3)
    
    # Запуск браузера с современным интерфейсом
    print("Запуск браузера...")
    try:
        # Пробуем использовать новый интерфейс
        import src.ui_modern as ui_modern
        ui_modern.start()
    except ImportError as e:
        print(f"Ошибка импорта современного UI: {e}")
        try:
            # Fallback на старый интерфейс
            import src.ui as ui
            ui.start()
        except ImportError as e2:
            print(f"Ошибка импорта UI: {e2}")
            # Fallback на webview
            try:
                import webview
                webview.create_window('Лёгкий браузер с VLESS VPN', 'https://www.google.com')
                webview.start()
            except ImportError:
                print("Webview не установлен. Установите: pip install pywebview")


if __name__ == '__main__':
    main()
