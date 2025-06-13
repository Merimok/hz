# Логирование Focus Browser

## Описание

Focus Browser автоматически создает логи работы браузера и sing-box VPN в папке `logs/`.

## Структура логов

### Браузер логи
- `focus_browser_YYYY-MM-DD.log` - основные логи браузера по дням
- Содержат информацию о:
  - Запуске/остановке приложения
  - Навигации по сайтам
  - Инициализации WebView
  - Работе с favicon
  - Очистке кэша

### sing-box логи
- `sing-box.log` - логи VPN соединения
- Содержат информацию о:
  - Статусе подключения к серверу
  - Трафике через прокси
  - Ошибках соединения

## Пример лог записи

```
2025-06-13 10:30:15.123 [INFO] FocusBrowser: === Focus Browser v1.0.3 Starting ===
2025-06-13 10:30:15.456 [INFO] FocusBrowser: Initializing Focus Browser
2025-06-13 10:30:15.789 [INFO] FocusBrowser: Starting VPN initialization...
2025-06-13 10:30:16.012 [INFO] FocusBrowser: sing-box started with PID: 1234
2025-06-13 10:30:16.345 [INFO] FocusBrowser: VPN connected to 94.131.110.172:23209
2025-06-13 10:30:16.678 [INFO] FocusBrowser: Initializing WebView...
2025-06-13 10:30:17.901 [INFO] FocusBrowser: Navigation successful: https://www.perplexity.ai
```

## Настройка логирования

Логирование настраивается автоматически при запуске приложения. Уровень логирования: INFO.

## Ротация логов

Логи браузера создаются по дням. Старые логи нужно удалять вручную или настроить автоматическую очистку.

## Отладка

Для отладки проблем:
1. Проверьте последние записи в `focus_browser_*.log`
2. Проверьте логи sing-box в `sing-box.log` 
3. Обратите внимание на ошибки [ERROR] и предупреждения [WARNING]
