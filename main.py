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
import atexit  # For cleanup on exit
import importlib  # For dynamic UI module loading
import argparse  # CLI arguments parsing
import time  # For delays and retry
import platform
import ctypes
import pystray  # Windows tray icon
from PIL import Image, ImageDraw

# Парсер аргументов
parser = argparse.ArgumentParser(description='Ultra-Modern Browser with VLESS VPN')
parser.add_argument('--no-vpn', action='store_true', help='Skip VPN (Xray) startup')
args = parser.parse_args()

# Создаем папку для логов если её нет
os.makedirs('logs', exist_ok=True)

# Добавляем текущую папку в PYTHONPATH для импорта src модулей  
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем систему логирования
from src.logger import browser_logger, log_exception


# Store Xray process globally for cleanup
global_xray_process = None  # Store Xray process for termination

UI_MODULES = [
    'src.ui_win11',      # Оптимизированный интерфейс для Windows 11
    'src.ui_ultra_modern',
    'src.ui_modern_fixed',
    'src.ui_modern',
    'src.ui',
    'src.ui_simple'
]


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
                uri = ''
    else:
        browser_logger.info("VLESS URI загружен из переменной окружения")
    
    if uri:
        browser_logger.info(f"VLESS URI успешно загружен (длина: {len(uri)} символов)")
    
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
            browser_logger.info(f"Парсинг URI: {uri}")
            
            # Извлекаем ID (username)
            if parsed.username:
                cfg['id'] = parsed.username
                browser_logger.debug(f"ID: {cfg['id']}")
            
            # Извлекаем адрес и порт
            if parsed.hostname:
                cfg['address'] = parsed.hostname
                browser_logger.debug(f"Адрес: {cfg['address']}")
            
            if parsed.port:
                cfg['port'] = parsed.port
                browser_logger.debug(f"Порт: {cfg['port']}")
            
            # Парсим параметры запроса
            qs = parse_qs(parsed.query)
            if 'fp' in qs:
                cfg['fp'] = qs['fp'][0]
                browser_logger.debug(f"Fingerprint: {cfg['fp']}")
            if 'pbk' in qs:
                cfg['pbk'] = qs['pbk'][0]
                browser_logger.debug(f"Public Key: {cfg['pbk'][:20]}...")
            if 'sni' in qs:
                cfg['sni'] = qs['sni'][0]
                browser_logger.debug(f"SNI: {cfg['sni']}")
            if 'sid' in qs:
                cfg['sid'] = qs['sid'][0]
                browser_logger.debug(f"Short ID: {cfg['sid']}")
                
        except Exception as e:
            browser_logger.error(f"Ошибка парсинга VLESS URI: {e}; используются значения по умолчанию")
    else:
        browser_logger.warning("VLESS URI не найден, используются значения по умолчанию")

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
    
    browser_logger.info(f"Создание конфигурации для сервера {cfg['address']}:{cfg['port']}")
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    browser_logger.info("Конфигурация config.json успешно создана")


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
        browser_logger.info('Загрузка Xray-core через urllib.request')
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
        
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
        browser_logger.warning("Xray не доступен, пропуск VPN")
        return
    # Пытаемся запустить Xray с retry
    retries = 3
    for attempt in range(1, retries+1):
        try:
            browser_logger.info(f"Запуск Xray (попытка {attempt}): {xray_path}")
            global global_xray_process
            global_xray_process = subprocess.Popen([xray_path, 'run', '-c', 'config.json'])
            browser_logger.info(f"Xray запущен с PID: {global_xray_process.pid}")
            return
        except Exception as e:
            browser_logger.error(f"Ошибка запуска Xray (попытка {attempt}): {e}")
            time.sleep(1)
    browser_logger.critical("Не удалось запустить Xray после нескольких попыток")

# Windows 11: DPI awareness and hide console
if platform.system() == 'Windows':
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
    except Exception:
        pass

# Create tray icon image
def _create_tray_image():
    width = 64; height = 64
    image = Image.new('RGB', (width, height), 'black')
    dc = ImageDraw.Draw(image)
    dc.rectangle((0, height//2, width, height), fill='white')
    return image

# Quit handler for tray menu
def _on_quit(icon, item):
    global global_xray_process
    if global_xray_process:
        global_xray_process.terminate()
    icon.stop()
    sys.exit(0)

# Initialize tray icon
threading.Thread(target=lambda: pystray.Icon(
    'UltraModernBrowser', _create_tray_image(), 'UltraModernBrowser',
    menu=pystray.Menu(pystray.MenuItem('Quit', _on_quit))
).run(), daemon=True).start()

def main():
    """Главная функция приложения Ultra-Modern Browser v4.0.0."""
    browser_logger.info("=== ЗАПУСК УЛЬТРА-СОВРЕМЕННОГО БРАУЗЕРА v4.0.0 ===")
    
    try:
        # Загрузка и проверка VLESS URI
        browser_logger.info("Этап 1: Загрузка VLESS URI")
        uri = get_vless_uri()
        if not uri:
            browser_logger.warning("VLESS URI не настроен")
        
        # Генерация конфигурации
        browser_logger.info("Этап 2: Генерация конфигурации")
        generate_config(uri)

        # Настройка прокси для SOCKS
        browser_logger.info("Этап 3: Настройка прокси")
        if not args.no_vpn:
            os.environ['HTTP_PROXY'] = 'socks5://127.0.0.1:1080'
            os.environ['HTTPS_PROXY'] = 'socks5://127.0.0.1:1080'
        else:
            browser_logger.info("VPN пропущен по аргументу --no-vpn")

        # Запуск Xray в фоновом режиме
        browser_logger.info("Этап 4: Запуск Xray")
        if not args.no_vpn:
            threading.Thread(target=start_xray, daemon=True).start()
            atexit.register(lambda: global_xray_process and global_xray_process.terminate())
        else:
            browser_logger.info("Пропускаем старт Xray (VPN)")

         # Небольшая задержка для запуска Xray
        import time; time.sleep(2)

        # Запуск браузера с каскадной системой UI v4.0.0
        browser_logger.info("Этап 5: Запуск Ultra-Modern Browser v4.0.0...")
        for module_name in UI_MODULES:
            try:
                browser_logger.info(f"Попытка запуска {module_name}")
                module = importlib.import_module(module_name)
                module.start()
                return
            except Exception as e:
                log_exception(browser_logger, e, module_name)
                continue
        # Если ни один модуль не запустился
        browser_logger.critical("Все UI интерфейсы недоступны. Завершение работы.")
        message = "Не удалось запустить ни один интерфейс. Установите зависимости: pip install pywebview PyQt5"
        print(f"Ошибка: {message}")
        # Windows MessageBox notification
        if platform.system() == 'Windows':
            ctypes.windll.user32.MessageBoxW(None, message, "Ultra-Modern Browser", 0)
        sys.exit(1)
        
    except Exception as e:
        log_exception(browser_logger, e, "main")
        print(f"\nКритическая ошибка в main(): {e}")
        print("\nНажмите Enter для выхода...")
        input()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрограмма завершена пользователем")
    except Exception as e:
        print(f"\nНеожиданная ошибка: {e}")
        print("\nНажмите Enter для выхода...")
        input()
