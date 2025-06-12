"""
Base Browser API - Унифицированный API для всех UI модулей
Ultra-Modern Browser v4.0.0
"""

import json
import os
from urllib.parse import quote_plus
import webview
import inspect
from typing import Optional
from src.logger import browser_logger, log_exception


class BaseBrowserApi:
    """Базовый API класс для всех браузерных интерфейсов."""
    
    def __init__(self):
        self.current_window: Optional[webview.Window] = None
        self.home_url = "https://www.google.com"
        
    def set_window(self, window: webview.Window):
        """Устанавливает ссылку на окно webview."""
        self.current_window = window
        browser_logger.debug(f"Установлено окно webview: {window}")
        
    def _ensure_window(self):
        """Проверяет наличие окна."""
        if not self.current_window:
            browser_logger.warning("Окно webview не установлено")
            return False
        return True
        
    def navigate(self, url: str):
        """Навигация по URL."""
        if not url:
            return
            
        try:
            # Если не начинается с http/https, делаем поиск в Google
            if not url.startswith(('http://', 'https://')):
                if '.' not in url or ' ' in url:
                    # Это поисковый запрос
                    url = f"https://www.google.com/search?q={quote_plus(url)}"
                else:
                    # Добавляем https://
                    url = f"https://{url}"
            
            browser_logger.info(f"Навигация на: {url}")
            
            if self._ensure_window():
                self.current_window.load_url(url)
                
        except Exception as e:
            log_exception(browser_logger, e, "navigate")
    
    def go_back(self):
        """Возврат назад."""
        try:
            if self._ensure_window():
                # В pywebview нет встроенной истории, возвращаемся на домашнюю
                browser_logger.info("Переход назад (возврат на главную)")
                self.current_window.load_url(self.home_url)
        except Exception as e:
            log_exception(browser_logger, e, "go_back")
    
    def go_forward(self):
        """Переход вперед."""
        try:
            if self._ensure_window():
                # В pywebview нет встроенной истории, переходим на главную
                browser_logger.info("Переход вперед (возврат на главную)")
                self.current_window.load_url(self.home_url)
        except Exception as e:
            log_exception(browser_logger, e, "go_forward")
    
    def refresh(self):
        """Обновление страницы."""
        try:
            if self._ensure_window():
                browser_logger.info("Обновление страницы")
                self.current_window.reload()
        except Exception as e:
            log_exception(browser_logger, e, "refresh")
    
    def go_home(self):
        """Переход на домашнюю страницу."""
        try:
            browser_logger.info("Переход на домашнюю страницу")
            self.navigate(self.home_url)
        except Exception as e:
            log_exception(browser_logger, e, "go_home")
    
    def focus_address_bar(self):
        """Фокус на адресную строку (Ctrl+L)."""
        try:
            browser_logger.debug("Фокус на адресную строку")
            # JavaScript команда будет вызвана из UI
            return True
        except Exception as e:
            log_exception(browser_logger, e, "focus_address_bar")
            return False


def create_webview_window_safe(title: str, html: str, api_instance: BaseBrowserApi, **kwargs):
    """Безопасное создание окна webview с обратной совместимостью."""
    try:
        browser_logger.info(f"Создание окна webview: {title}")
        
        # Проверяем версию pywebview для обратной совместимости
        start_signature = inspect.signature(webview.start)
        supports_api_param = 'api' in start_signature.parameters
        
        browser_logger.debug(f"PyWebview поддерживает api параметр: {supports_api_param}")
        
        # Создаем окно
        if supports_api_param:
            # Для pywebview 4.0+ API передается в create_window через js_api
            window = webview.create_window(title, html, js_api=api_instance, **kwargs)
        else:
            # Для старых версий API передается отдельно
            window = webview.create_window(title, html, **kwargs)
        
        # Связываем API с окном
        api_instance.set_window(window)
        
        return window, supports_api_param
        
    except Exception as e:
        log_exception(browser_logger, e, "create_webview_window_safe")
        raise


def start_webview_safe(api_instance: BaseBrowserApi, supports_api_param: bool = None):
    """Безопасный запуск webview с обратной совместимостью."""
    try:
        if supports_api_param is None:
            start_signature = inspect.signature(webview.start)
            supports_api_param = 'api' in start_signature.parameters
        
        if supports_api_param:
            # Новая версия pywebview (4.0+)
            browser_logger.debug("Запуск с новым API pywebview 4.0+")
            webview.start(api=api_instance, debug=False, http_server=True)
        else:
            # Старая версия pywebview (3.x)
            browser_logger.debug("Запуск с legacy API pywebview 3.x")
            webview.start(debug=False, http_server=True)
            
        browser_logger.info("✅ Webview успешно запущен")
        
    except Exception as e:
        log_exception(browser_logger, e, "start_webview_safe")
        raise


def load_bookmarks():
    """Загружает закладки из файла."""
    try:
        bookmarks_path = os.path.join('resources', 'bookmarks.json')
        if os.path.exists(bookmarks_path):
            with open(bookmarks_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Дефолтные закладки
            default_bookmarks = [
                {"name": "🔍 Google", "url": "https://www.google.com"},
                {"name": "📺 YouTube", "url": "https://www.youtube.com"},
                {"name": "🌐 2IP", "url": "https://2ip.ru"},
                {"name": "📧 Gmail", "url": "https://gmail.com"},
                {"name": "🔧 GitHub", "url": "https://github.com"}
            ]
            browser_logger.info("Используются дефолтные закладки")
            return default_bookmarks
    except Exception as e:
        log_exception(browser_logger, e, "load_bookmarks")
        return []


# Общие константы для всех UI модулей
COMMON_SHORTCUTS = {
    'Ctrl+T': 'Новая вкладка',
    'Ctrl+W': 'Закрыть вкладку', 
    'Ctrl+R': 'Обновить',
    'Ctrl+L': 'Фокус на адресную строку',
    'Ctrl+D': 'Добавить в закладки',
    'Ctrl+H': 'История',
    'F5': 'Обновить',
    'F11': 'Полный экран',
    'Escape': 'Остановить загрузку'
}

COMMON_CSS_VARIABLES = """
:root {
    --primary-color: #6366f1;
    --primary-hover: #5855eb;
    --secondary-color: #f1f5f9;
    --text-color: #1e293b;
    --text-light: #64748b;
    --border-color: #e2e8f0;
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --error-color: #ef4444;
    --bg-color: #ffffff;
    --bg-secondary: #f8fafc;
    --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    --border-radius: 8px;
    --font-family: 'Inter', system-ui, -apple-system, sans-serif;
}
"""
