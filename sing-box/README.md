# sing-box VPN Configuration

## Предустановленная конфигурация

Focus Browser поставляется с предустановленной VLESS конфигурацией:

```
Server: 94.131.110.172:23209
UUID: 331564911
Protocol: VLESS + Reality
SNI: yahoo.com
Local Proxy: 127.0.0.1:1080 (SOCKS5/HTTP)
```

Полный VLESS URI сохранен в `/config/vless.txt`:
```
vless://331564911@94.131.110.172:23209?type=tcp&security=reality&pbk=EhZf6JqOLErCdliMk1UBlpojo3cfw244QWtoZ-qUFTc&fp=random&sni=yahoo.com&sid=68c55e5189f67c90&spx=#Tannim-DE
```

## Установка sing-box

1. Скачайте sing-box для Windows: https://github.com/SagerNet/sing-box/releases
2. Извлеките `sing-box.exe` в папку `sing-box/`
3. sing-box автоматически запустится с предустановленной конфигурацией

## Конфигурация

Файл `config.json` содержит готовую конфигурацию со всеми необходимыми параметрами:
- VLESS outbound с Reality TLS
- Mixed inbound на порту 1080
- Логирование в `logs/sing-box.log`
- Автоматическая маршрутизация трафика

## Использование

После установки sing-box.exe браузер автоматически:
1. Запустит sing-box с предустановленной конфигурацией
2. Установит системный прокси на 127.0.0.1:1080  
3. Проверит соединение с сервером
4. Начнет логирование активности

## Логи

Все логи sing-box сохраняются в файл `logs/sing-box.log` для диагностики соединения.

## Поддерживаемые функции

- VLESS протокол с Reality TLS
- SOCKS5 и HTTP прокси
- Автоматическая маршрутизация
- Логирование соединений
- Автоматический запуск/остановка
