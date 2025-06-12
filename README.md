# 🌐 Лёгкий браузер с VLESS VPN v2.2.0

![Status](https://img.shields.io/badge/Status-Production%20Ready-green)
![Version](https://img.shields.io/badge/Version-v2.2.0-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey)

Легкий браузер с встроенной поддержкой VLESS VPN через Xray-core. Современный интерфейс с Material Design и автоматической настройкой VPN подключения.

## ✨ Особенности

- 🔐 **VLESS + Reality VPN** - Безопасное подключение через Xray-core
- 🎨 **Современный UI** - Material Design с градиентными эффектами  
- 🔄 **Fallback система** - 4 уровня резервных интерфейсов
- ⚡ **Автонастройка** - Автоматическая загрузка и настройка Xray
- 🌍 **Навигация** - Полнофункциональный браузер с закладками
- 🛡️ **Надежность** - Комплексная обработка ошибок

## 🚀 Быстрый старт

### Windows (Готовый исполняемый файл)
1. Скачайте `lightweight-browser-vless-v2.2.0-windows.zip` из [Releases](../../releases)
2. Распакуйте архив
3. Запустите `lightweight-browser-vless-v2.2.0.exe`

### Из исходного кода
```bash
# Клонируйте репозиторий
git clone <repository-url>
cd hz

# Установите зависимости
pip install -r requirements.txt

# Запустите браузер
python main.py
```

## ⚙️ Конфигурация

### VLESS URI
Поместите ваш VLESS URI в файл `config/vless.txt`:
```
vless://user@server:port?encryption=none&security=reality&sni=domain.com&...
```

### Закладки
Настройте закладки в `resources/bookmarks.json`:
```json
[
  {"name": "YouTube", "url": "https://www.youtube.com"},
  {"name": "2IP", "url": "https://2ip.ru"}
]
```

## 🧪 Тестирование

```bash
# Полный тест проекта
python test_comprehensive.py

# Тест pywebview совместимости  
python test_webview.py
```

## 🔒 Безопасность

- **VLESS + Reality** - Современное шифрование трафика
- **Local SOCKS Proxy** - Весь трафик через локальный прокси
- **No Data Collection** - Никаких логов пользовательской активности
- **Open Source** - Полностью открытый исходный код

## 🐛 Устранение неполадок

### Браузер не запускается
```bash
# Проверьте зависимости
pip install pywebview>=4.0.0

# Запустите с отладкой
python main.py
```

### VLESS не подключается
1. Проверьте URI в `config/vless.txt`
2. Убедитесь что сервер доступен
3. Проверьте логи Xray в консоли

---

**Made with ❤️ for secure and private browsing**

