# 🌐 Ultra-Modern Browser with VLESS VPN v4.0.0

![Status](https://img.shields.io/badge/Status-Production%20Ready-green)
![Version](https://img.shields.io/badge/Version-v4.0.0-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%2011-lightgrey)

Легкий браузер с встроенной поддержкой VLESS VPN через Xray-core. Современный интерфейс с Windows 11 интеграцией и автоматической настройкой VPN подключения. В версии 4.0.0 добавлена поддержка портативного режима.

## ✨ Особенности

- 🔐 **VLESS + Reality VPN** - Безопасное подключение через Xray-core
- 🎨 **Windows 11 UI** - Современный дизайн с поддержкой Windows 11
- 🔄 **Fallback система** - 5 уровней резервных интерфейсов
- ⚡ **Автонастройка** - Автоматическая загрузка и настройка Xray
- 🌍 **Навигация** - Полнофункциональный браузер с вкладками и закладками
- 🛡️ **Надежность** - Комплексная обработка ошибок
- 📦 **Portable Mode** - Портативный режим без установки

## 🚀 Быстрый старт

### Windows 11 (Портативная версия)
1. Скачайте `Ultra-Modern-Browser-v4.0.0-Portable.zip` из [Releases](../../releases)
2. Распакуйте архив в любую папку
3. Запустите `Launch-Browser.bat` для запуска приложения
2. Распакуйте архив
3. Запустите `lightweight-browser-vless-v2.2.0.exe`

### Из исходного кода
```bash
# Клонируйте репозиторий
git clone <repository-url>
cd hz

# Установите зависимости
pip install -r requirements.txt

# Скачайте Xray-core (обязательно!)
# Перейдите на https://github.com/XTLS/Xray-core/releases
# Скачайте Xray-windows-64.zip (для Windows) или соответствующую версию
# Извлеките xray.exe в папку bin/xray.exe

# Запустите браузер
python main.py
```

## 📦 Установка Xray-core

**Важно:** Для работы VPN необходим бинарный файл Xray-core.

### Автоматическая установка (Windows)
Приложение попытается автоматически скачать Xray при первом запуске.

### Ручная установка (рекомендуется)
1. Перейдите на https://github.com/XTLS/Xray-core/releases
2. Скачайте архив для вашей платформы:
   - Windows: `Xray-windows-64.zip`
   - Linux: `Xray-linux-64.zip`
   - macOS: `Xray-macos-64.zip`
3. Извлеките исполняемый файл в папку `bin/`:
   - Windows: `bin/xray.exe`
   - Linux/macOS: `bin/xray`
4. Убедитесь, что файл исполняемый (chmod +x для Linux/macOS)

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

