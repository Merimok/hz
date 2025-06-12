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
    except FileNotFoundError:
        print('Xray исполняемый файл не найден.')
    except Exception as e:
        print(f'Ошибка запуска Xray: {e}')


def main():
    """Главная функция приложения."""
    browser_logger.info("=== ЗАПУСК ЛЁГКОГО БРАУЗЕРА С VLESS VPN ===")
    
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
        
        # Запуск браузера с современным интерфейсом
        browser_logger.info("Этап 5: Запуск браузера...")
        
        try:
            # Пробуем использовать УЛЬТРА-СОВРЕМЕННЫЙ интерфейс
            browser_logger.info("Попытка запуска ui_ultra_modern")
            import src.ui_ultra_modern as ui_ultra_modern
            ui_ultra_modern.start()
        except Exception as e:
            log_exception(browser_logger, e, "ui_ultra_modern")
            try:
                # Пробуем использовать исправленный интерфейс
                browser_logger.info("Fallback на ui_modern_fixed")
                import src.ui_modern_fixed as ui_modern_fixed
                ui_modern_fixed.start()
            except Exception as e:
                log_exception(browser_logger, e, "ui_modern_fixed")
                try:
                    # Fallback на новый интерфейс
                    browser_logger.info("Fallback на ui_modern")
                    import src.ui_modern as ui_modern
                    ui_modern.start()
                except Exception as e:
                    log_exception(browser_logger, e, "ui_modern")
                    try:
                        # Fallback на старый интерфейс
                        browser_logger.info("Fallback на ui")
                        import src.ui as ui
                        ui.start()
                    except Exception as e:
                        log_exception(browser_logger, e, "ui")
                        try:
                            # Последний fallback на простой интерфейс
                            browser_logger.info("Fallback на ui_simple")
                            import src.ui_simple as ui_simple
                            ui_simple.start()
                        except Exception as e:
                            log_exception(browser_logger, e, "ui_simple")
                            browser_logger.critical("Все UI интерфейсы недоступны!")
                            print("Ошибка: Не удалось запустить ни один интерфейс")
                            print("Проверьте установку зависимостей: pip install pywebview>=4.0.0")
                            print("\nНажмите Enter для выхода...")
                            input()
                        
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
