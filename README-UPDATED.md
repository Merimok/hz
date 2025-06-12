# Лёгкий браузер с VLESS VPN

🚀 **Простой и эффективный браузер с встроенной поддержкой VLESS VPN**

Этот проект предоставляет минималистичное Python приложение, которое запускает браузер на основе webview и автоматически настраивает **Xray-core** с VLESS конфигурацией. Браузер маршрутизирует весь трафик через локальный VLESS прокси.

## 🌟 Особенности

- ✅ **Автоматическая загрузка Xray-core** - не требует ручной установки
- ✅ **Автогенерация конфигурации** из VLESS URI
- ✅ **Встроенные закладки** (YouTube, 2IP для проверки IP)
- ✅ **Простая навигация** с адресной строкой и кнопками
- ✅ **Google поиск** при вводе текста без протокола
- ✅ **CI/CD с GitHub Actions** для автоматической сборки
- ✅ **Стартовая страница Google** вместо example.com

## 📁 Структура проекта

```
project_root/
├── src/                    # Python модули
│   ├── main.py            # Альтернативная реализация с ensure_xray()
│   └── ui.py              # Интерфейс браузера
├── config/
│   └── vless.txt          # VLESS URI конфигурация
├── resources/
│   └── bookmarks.json     # Закладки (YouTube, 2IP)
├── bin/
│   └── xray.exe           # Xray-core (загружается автоматически)
├── tests/                 # Автоматические тесты
│   ├── __init__.py
│   └── test_main.py       # Тесты основных функций
├── .github/workflows/
│   ├── build.yml          # Оригинальный workflow (с проблемами)
│   └── build-fixed.yml    # Исправленный workflow
├── main.py                # Основной файл приложения
├── requirements.txt       # Python зависимости
├── config.json           # Автогенерируемая конфигурация Xray
└── README.md             # Эта документация
```

## 🚀 Использование

### Быстрый старт
1. **Настройте VLESS URI:**
   - Через переменную окружения: `export VLESS_URI="vless://..."`
   - Или отредактируйте `config/vless.txt`

2. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Запустите приложение:**
   ```bash
   python main.py
   ```

### Функции браузера
- **Навигация:** кнопки ← → ⟲ для навигации
- **Адресная строка:** введите URL или поисковый запрос
- **Закладки:** выпадающее меню с быстрым доступом
- **Автопрокси:** весь трафик автоматически через VLESS

## 🛠️ Сборка

### Автоматическая сборка (GitHub Actions)
- Push в репозиторий автоматически запускает сборку
- Результат: готовый `lightweight-browser-vless-windows.zip`
- Включает все необходимые файлы и Xray-core

### Ручная сборка
```bash
# Установка зависимостей
pip install pyinstaller pywebview

# Сборка исполняемого файла
pyinstaller --onefile --add-data "config;config" --add-data "resources;resources" --add-data "bin;bin" main.py
```

## 🧪 Тестирование

```bash
# Запуск всех тестов
python -m pytest tests/

# Запуск конкретного теста
python -m unittest tests.test_main.TestVLESSBrowser.test_generate_config_default
```

### Покрытие тестами
- ✅ Загрузка VLESS URI из разных источников
- ✅ Генерация конфигурации Xray
- ✅ Парсинг VLESS параметров
- ✅ Загрузка закладок
- ✅ Обработка ошибок

## 🔧 Конфигурация

### VLESS URI формат
```
vless://uuid@server:port?type=tcp&security=reality&pbk=public_key&fp=fingerprint&sni=server_name&sid=short_id
```

### Пример config/vless.txt
```
vless://331564911@94.131.110.172:23209?type=tcp&security=reality&pbk=EhZf6JqOLErCdliMk1UBlpojo3cfw244QWtoZ-qUFTc&fp=random&sni=yahoo.com&sid=68c55e5189f67c90&spx=#Tannim-DE
```

## ❗ Исправленные проблемы

### ✅ Что было исправлено:
1. **Автоматическая загрузка Xray** - добавлена функция `ensure_xray()`
2. **Правильная стартовая страница** - теперь Google вместо example.com
3. **Улучшенная обработка ошибок** - понятные сообщения пользователю
4. **Docstrings и комментарии** - код теперь документирован
5. **Исправлен CI/CD workflow** - убраны merge conflicts
6. **Добавлены тесты** - автоматическое тестирование ключевых функций
7. **requirements.txt** - явное указание зависимостей
8. **Поддержка config/vless.txt** - альтернативный путь к конфигурации

### 🔧 Технические улучшения:
- Использование полного пути к `xray.exe`
- Создание папки `bin/` при необходимости  
- Проверка успешности загрузки Xray
- Вывод PID процесса для отладки
- Правильное кодирование UTF-8 для файлов

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл `LICENSE` для подробностей.
