import os
import sys
import subprocess
import threading
import webview
import json
import urllib.request
import zipfile
import io
from urllib.parse import urlparse, parse_qs

# Создаем папку для логов если её нет
os.makedirs('logs', exist_ok=True)

# Добавляем текущую папку в PYTHONPATH для импорта src модулей  
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем систему логирования
from src.logger import browser_logger, log_exception


def get_vless_uri():
    """Загружает VLESS URI из переменной окружения или файла vless.txt."""
    browser_logger.info("Загрузка VLESS URI...")
    
    uri = os.getenv('VLESS_URI')
    if not uri:
        try:
            with open('vless.txt', 'r', encoding='utf-8') as f:
                uri = f.readline().strip()
            browser_logger.info("VLESS URI загружен из vless.txt")
        except FileNotFoundError:
            try:
                with open(os.path.join('config', 'vless.txt'), 'r', encoding='utf-8') as f:
                    uri = f.readline().strip()
                browser_logger.info("VLESS URI загружен из config/vless.txt")
            except FileNotFoundError:
                browser_logger.error("VLESS URI не найден. Проверьте файл vless.txt или переменную VLESS_URI")
                print("VLESS URI not found. Check vless.txt file or VLESS_URI environment variable")
                uri = ''
        else:
            browser_logger.info("VLESS URI загружен из переменной окружения")
    
    if uri:
        browser_logger.info(f"VLESS URI успешно загружен (длина: {len(uri)} символов)")
    
    return uri


def generate_config(uri: str):
    """Generate config.json configuration based on VLESS URI."""
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
    
    # Parse VLESS URI
    if uri and uri.startswith('vless://'):
        try:
            parsed = urlparse(uri)
            print(f"Parsing URI: {uri}")
            
            # Extract ID (username)
            if parsed.username:
                cfg['id'] = parsed.username
                print(f"ID: {cfg['id']}")
            
            # Extract address and port
            if parsed.hostname:
                cfg['address'] = parsed.hostname
                print(f"Address: {cfg['address']}")
            
            if parsed.port:
                cfg['port'] = parsed.port
                print(f"Port: {cfg['port']}")
            
            # Parse query parameters
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
            print(f"Error parsing VLESS URI: {e}")
            print("Using default values")
    else:
        print("VLESS URI not found, using default values")

    # Generate proper configuration for Xray-core
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
    
    print(f"Creating configuration for server {cfg['address']}:{cfg['port']}")
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print("Configuration config.json successfully created")


def ensure_xray():
    """Check for xray.exe presence and download if necessary."""
    xray_path = os.path.join('bin', 'xray.exe')
    
    # Create bin folder if it doesn't exist
    os.makedirs('bin', exist_ok=True)
    
    if os.path.exists(xray_path):
        print(f"Xray found: {xray_path}")
        return xray_path
    
    print("Xray not found. Downloading from GitHub...")
    url = 'https://github.com/XTLS/Xray-core/releases/latest/download/Xray-windows-64.zip'
    
    try:
        print('Downloading Xray-core...')
        data = urllib.request.urlopen(url).read()
        
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            for name in zf.namelist():
                if name.endswith('xray.exe'):
                    with open(xray_path, 'wb') as f:
                        f.write(zf.read(name))
                    print(f"Xray successfully downloaded: {xray_path}")
                    return xray_path
                    
        print("xray.exe not found in archive")
        return None
        
    except Exception as e:
        print(f"Error downloading Xray: {e}")
        return None


def start_xray():
    """Start Xray-core with binary download if necessary."""
    xray_path = ensure_xray()
    if not xray_path:
        print("Failed to obtain Xray-core. Continuing without VPN.")
        return
    
    try:
        print(f"Starting Xray: {xray_path}")
        process = subprocess.Popen([xray_path, 'run', '-c', 'config.json'])
        print(f"Xray started with PID: {process.pid}")
    except FileNotFoundError:
        print('Xray executable file not found.')
    except Exception as e:
        print(f'Error starting Xray: {e}')


def main():
    """Главная функция приложения Ultra-Modern Browser v4.0.0."""
    browser_logger.info("=== ЗАПУСК УЛЬТРА-СОВРЕМЕННОГО БРАУЗЕРА v4.0.0 (Windows Compatible) ===")
    print("=== Ultra-Modern Browser with VLESS VPN v4.0.0 ===")
    
    try:
        # Загрузка и проверка VLESS URI
        browser_logger.info("Этап 1: Загрузка VLESS URI")
        uri = get_vless_uri()
        if not uri:
            browser_logger.warning("VLESS URI не настроен")
            print("Warning: VLESS URI not configured")
        
        # Генерация конфигурации
        browser_logger.info("Этап 2: Генерация конфигурации")
        generate_config(uri)

        # Настройка прокси для SOCKS
        browser_logger.info("Этап 3: Настройка прокси")
        os.environ['HTTP_PROXY'] = 'socks5://127.0.0.1:1080'
        os.environ['HTTPS_PROXY'] = 'socks5://127.0.0.1:1080'
        browser_logger.debug("Прокси настроен: SOCKS5://127.0.0.1:1080")

        # Запуск Xray в фоновом режиме
        browser_logger.info("Этап 4: Запуск Xray")
        threading.Thread(target=start_xray, daemon=True).start()
        
        # Небольшая задержка для запуска Xray
        browser_logger.info("Ожидание запуска Xray (2 секунды)...")
        import time
        time.sleep(2)
        
        # Запуск браузера с каскадной системой UI v4.0.0
        browser_logger.info("Этап 5: Запуск Ultra-Modern Browser v4.0.0...")
        
        try:
            # Уровень 1: УЛЬТРА-СОВРЕМЕННЫЙ интерфейс с Material Design 3
            browser_logger.info("🎨 Попытка запуска ui_ultra_modern (Material Design 3)")
            print("Attempting to load: Ultra-Modern Material Design 3 UI v4.0.0")
            import src.ui_ultra_modern as ui_ultra_modern
            ui_ultra_modern.start()
        except Exception as e:
            log_exception(browser_logger, e, "ui_ultra_modern")
            print(f"Failed to import src.ui_ultra_modern: {e}")
            try:
                # Уровень 2: Исправленный современный интерфейс с вкладками
                browser_logger.info("🔧 Fallback на ui_modern_fixed (Fixed Modern + Tabs)")
                print("Attempting to load: Modern UI with fixed pywebview 4.0+ compatibility")
                import src.ui_modern_fixed as ui_modern_fixed
                ui_modern_fixed.start()
            except Exception as e:
                log_exception(browser_logger, e, "ui_modern_fixed")
                print(f"Failed to import src.ui_modern_fixed: {e}")
                try:
                    # Уровень 3: Обновленный современный интерфейс v4.0.0
                    browser_logger.info("✨ Fallback на ui_modern (Gradient Design v4.0.0)")
                    print("Attempting to load: Alternative modern UI v4.0.0")
                    import src.ui_modern as ui_modern
                    ui_modern.start()
                except Exception as e:
                    log_exception(browser_logger, e, "ui_modern")
                    print(f"Failed to import src.ui_modern: {e}")
                    try:
                        # Уровень 4: Базовый интерфейс с обновленным API
                        browser_logger.info("🔧 Fallback на ui (Basic UI v4.0.0)")
                        print("Attempting to load: Basic UI with unified API v4.0.0")
                        import src.ui as ui
                        ui.start()
                    except Exception as e:
                        log_exception(browser_logger, e, "ui")
                        print(f"Failed to import src.ui: {e}")
                        try:
                            # Уровень 5: Простой интерфейс (всегда работает)
                            browser_logger.info("🛡️ Fallback на ui_simple (Tkinter Fallback)")
                            print("Attempting to load: Fallback UI with Tkinter (no pywebview required)")
                            import src.ui_simple as ui_simple
                            ui_simple.start()
                        except Exception as e:
                            log_exception(browser_logger, e, "ui_simple")
                            print(f"Failed to import src.ui_simple: {e}")
                            browser_logger.critical("🚨 ВСЕ UI ИНТЕРФЕЙСЫ НЕДОСТУПНЫ!")
                            print("ERROR: All UI modules failed to load!")
                            print("Please check:")
                            print("1. pywebview installation: pip install pywebview>=3.6")
                            print("2. tkinter availability (usually included with Python)")
                            print("3. System dependencies for GUI applications")
                            print("\nPress Enter to exit...")
                            input()
                        
    except Exception as e:
        log_exception(browser_logger, e, "main")
        print(f"\nКритическая ошибка в main(): {e}")
        print("\nPress Enter to exit...")
        input()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрограмма завершена пользователем")
    except Exception as e:
        print(f"\nНеожиданная ошибка: {e}")
        print("\nPress Enter to exit...")
        input()
