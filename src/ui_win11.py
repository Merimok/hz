"""
Windows 11 UI модуль с оптимизированными элементами навигации.
Содержит верхнюю панель с навигационными кнопками и адресной строкой.
"""
import json
import os
from urllib.parse import quote_plus
import webview
import platform
import ctypes
from src.core.tab_manager import TabManager
from src.logger import browser_logger, log_exception


class Win11BrowserApi:
    """API для Windows 11 браузера с продвинутым TabManager."""
    
    def __init__(self):
        self.current_window = None
        self.tab_manager = TabManager()
        
        # Создаем первую вкладку по умолчанию
        self.tab_manager.create_tab("https://www.google.com", "🔍 Поиск Google")
        
    def set_window(self, window):
        """Устанавливает ссылку на окно webview."""
        self.current_window = window
        
    def navigate(self, url):
        """Навигация по URL в активной вкладке."""
        if not self.current_window:
            browser_logger.error("Window not initialized")
            return {'success': False, 'error': 'Window not initialized'}
            
        # Если URL не содержит протокол, добавляем https://
        if not url.startswith(('http://', 'https://')):
            if '.' in url and ' ' not in url:
                url = 'https://' + url
            else:
                url = 'https://www.google.com/search?q=' + quote_plus(url)
        
        # Обновляем URL активной вкладки
        active_tab = self.tab_manager.get_active_tab()
        if active_tab:
            active_tab.url = url
            # Получаем title страницы (упрощенно)
            domain = url.split('/')[2] if '://' in url else url
            active_tab.title = f"🌐 {domain}"
                
        browser_logger.info(f"Навигация к: {url}")
        self.current_window.load_url(url)
        
        # Обновляем URL в адресной строке
        self.current_window.evaluate_js(f"document.getElementById('url-input').value = '{url}'")
        
        return {'success': True, 'url': url}
        
    def go_back(self):
        """История назад."""
        browser_logger.info("История назад")
        if self.current_window:
            self.current_window.evaluate_js('window.history.back()')
            # Обновляем URL в адресной строке после небольшой задержки
            self.current_window.evaluate_js('''
                setTimeout(() => {
                    document.getElementById('url-input').value = window.location.href;
                }, 100);
            ''')
            return {'success': True}
        return {'success': False, 'error': 'Window not initialized'}
        
    def go_forward(self):
        """История вперед."""
        browser_logger.info("История вперед")
        if self.current_window:
            self.current_window.evaluate_js('window.history.forward()')
            # Обновляем URL в адресной строке после небольшой задержки
            self.current_window.evaluate_js('''
                setTimeout(() => {
                    document.getElementById('url-input').value = window.location.href;
                }, 100);
            ''')
            return {'success': True}
        return {'success': False, 'error': 'Window not initialized'}
        
    def refresh(self):
        """Обновить страницу."""
        browser_logger.info("Обновление страницы")
        if self.current_window:
            self.current_window.evaluate_js('window.location.reload()')
            return {'success': True}
        return {'success': False, 'error': 'Window not initialized'}
        
    def get_current_url(self):
        """Получить текущий URL."""
        browser_logger.info("Получение текущего URL")
        if self.current_window:
            url = self.current_window.evaluate_js('window.location.href')
            # Обновляем URL в адресной строке
            self.current_window.evaluate_js(f"document.getElementById('url-input').value = '{url}'")
            return {'success': True, 'url': url}
        return {'success': False, 'error': 'Window not initialized'}
    
    # === МЕТОДЫ ДЛЯ РАБОТЫ С ВКЛАДКАМИ ===
    
    def create_new_tab(self, url="https://www.google.com"):
        """Создает новую вкладку."""
        domain = url.split('/')[2] if '://' in url else "Новая вкладка"
        tab = self.tab_manager.create_tab(url, f"🌐 {domain}")
        browser_logger.info(f"Создана вкладка: {tab.id}")
        
        # Переключаемся на новую вкладку
        self.switch_tab(tab.id)
        
        return {'success': True, 'tab_id': tab.id, 'url': url}
        
    def close_tab(self, tab_id):
        """Закрывает вкладку."""
        browser_logger.info(f"Закрытие вкладки: {tab_id}")
        
        # Если это единственная вкладка, создаем новую перед закрытием
        if len(self.tab_manager.tabs) <= 1:
            self.create_new_tab()
        
        # Закрываем вкладку
        result = self.tab_manager.close_tab(tab_id)
        
        if result:
            # Переключаемся на следующую активную вкладку
            active_tab = self.tab_manager.get_active_tab()
            if active_tab:
                self.navigate(active_tab.url)
                
        return {'success': result, 'tabs': self.get_tabs()}
        
    def switch_tab(self, tab_id):
        """Переключает активную вкладку."""
        browser_logger.info(f"Переключение на вкладку: {tab_id}")
        
        # Переключаем активную вкладку
        result = self.tab_manager.switch_tab(tab_id)
        
        # Если успешно переключились, обновляем URL
        if result:
            active_tab = self.tab_manager.get_active_tab()
            if active_tab:
                self.navigate(active_tab.url)
                
        return {'success': result, 'tabs': self.get_tabs()}
        
    def get_tabs(self):
        """Возвращает список вкладок."""
        return self.tab_manager.get_tabs_dict()


def start():
    """Запускает браузер с интерфейсом Windows 11."""
    browser_logger.info("🚀 Запуск браузера с интерфейсом Windows 11...")
    
    # Настраиваем Windows 11 специфичные параметры
    if platform.system() == 'Windows':
        try:
            # DPI awareness
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
            
            # Скрываем консоль
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            if hwnd:
                ctypes.windll.user32.ShowWindow(hwnd, 0)
        except Exception as e:
            log_exception(browser_logger, e, "Windows 11 setup")
    
    # Загружаем закладки
    bookmarks = []
    try:
        with open('config/bookmarks.json', 'r', encoding='utf-8') as f:
            bookmarks = json.load(f)
        browser_logger.info(f"Загружено {len(bookmarks)} закладок")
    except Exception as e:
        browser_logger.warning("Файл закладок не найден, используются закладки по умолчанию")
        bookmarks = [
            {"name": "Google", "url": "https://www.google.com"},
            {"name": "2IP", "url": "https://2ip.ru"},
            {"name": "YouTube", "url": "https://www.youtube.com"}
        ]
    
    # HTML шаблон для интерфейса
    html = """<!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Windows 11 Browser</title>
        <style>
            /* === ШРИФТЫ И ПЕРЕМЕННЫЕ === */
            @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;500;600&display=swap');
            @import url('https://fonts.googleapis.com/icon?family=Material+Icons+Round');
            
            :root {
                /* Windows 11 цвета */
                --win11-bg: #f6f6f6;
                --win11-primary: #0067c0;
                --win11-primary-hover: #0078d4;
                --win11-text: #000000;
                --win11-text-secondary: #616161;
                --win11-border: #d1d1d1;
                --win11-surface: #ffffff;
                --win11-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
                --win11-radius: 8px;
                --win11-transition: all 0.2s ease-in-out;
            }
            
            /* === ОСНОВНЫЕ СТИЛИ === */
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Segoe UI', sans-serif;
            }
            
            body {
                background: var(--win11-bg);
                height: 100vh;
                overflow: hidden;
                color: var(--win11-text);
                display: flex;
                flex-direction: column;
            }
            
            /* === ВЕРХНЯЯ ПАНЕЛЬ НАВИГАЦИИ (contextMenuStrip) === */
            .navigation-bar {
                background: var(--win11-surface);
                padding: 8px 12px;
                display: flex;
                align-items: center;
                gap: 8px;
                border-bottom: 1px solid var(--win11-border);
                box-shadow: var(--win11-shadow);
                z-index: 100;
            }
            
            .nav-button {
                background: transparent;
                border: none;
                border-radius: var(--win11-radius);
                width: 36px;
                height: 36px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: var(--win11-transition);
                color: var(--win11-text-secondary);
            }
            
            .nav-button:hover {
                background: rgba(0, 0, 0, 0.05);
                color: var(--win11-text);
            }
            
            .nav-button:active {
                background: rgba(0, 0, 0, 0.1);
            }
            
            .nav-button .material-icons-round {
                font-size: 20px;
            }
            
            .url-container {
                flex: 1;
                position: relative;
                height: 36px;
                margin: 0 8px;
            }
            
            .url-input {
                width: 100%;
                height: 100%;
                border: 1px solid var(--win11-border);
                border-radius: var(--win11-radius);
                padding: 0 12px 0 36px;
                font-size: 14px;
                transition: var(--win11-transition);
                outline: none;
            }
            
            .url-input:focus {
                border-color: var(--win11-primary);
                box-shadow: 0 0 0 2px rgba(0, 103, 192, 0.2);
            }
            
            .url-icon {
                position: absolute;
                left: 10px;
                top: 50%;
                transform: translateY(-50%);
                color: var(--win11-text-secondary);
                font-size: 16px;
            }
            
            /* === ВКЛАДКИ === */
            .tabs-container {
                background: var(--win11-bg);
                display: flex;
                padding: 4px 8px 0;
                gap: 4px;
                overflow-x: auto;
                scrollbar-width: none;
            }
            
            .tabs-container::-webkit-scrollbar {
                display: none;
            }
            
            .tab {
                background: rgba(255, 255, 255, 0.7);
                border: 1px solid var(--win11-border);
                border-bottom: none;
                border-radius: 8px 8px 0 0;
                padding: 8px 16px;
                display: flex;
                align-items: center;
                gap: 8px;
                min-width: 160px;
                max-width: 200px;
                cursor: pointer;
                transition: var(--win11-transition);
                position: relative;
                backdrop-filter: blur(10px);
            }
            
            .tab.active {
                background: white;
                border-color: var(--win11-border);
            }
            
            .tab-icon {
                font-size: 16px;
                color: var(--win11-text-secondary);
            }
            
            .tab-title {
                flex: 1;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                font-size: 13px;
            }
            
            .tab-close {
                width: 16px;
                height: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                font-size: 14px;
                opacity: 0.6;
                transition: var(--win11-transition);
            }
            
            .tab:hover .tab-close {
                opacity: 1;
            }
            
            .tab-close:hover {
                background: rgba(0, 0, 0, 0.1);
            }
            
            .new-tab-btn {
                background: transparent;
                border: none;
                width: 28px;
                height: 28px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-left: 4px;
                border-radius: var(--win11-radius);
                cursor: pointer;
            }
            
            .new-tab-btn:hover {
                background: rgba(0, 0, 0, 0.05);
            }
            
            /* === ОСНОВНОЙ КОНТЕНТ === */
            .content-area {
                flex: 1;
                background: white;
                position: relative;
                overflow: hidden;
                display: flex;
                flex-direction: column;
            }
            
            /* === СТАТУСНАЯ СТРОКА === */
            .status-bar {
                background: var(--win11-surface);
                border-top: 1px solid var(--win11-border);
                padding: 6px 16px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                font-size: 12px;
                color: var(--win11-text-secondary);
            }
            
            /* === АДАПТИВНЫЕ СТИЛИ === */
            @media (max-width: 600px) {
                .navigation-bar {
                    padding: 8px;
                    gap: 4px;
                }
                
                .url-container {
                    margin: 0 4px;
                }
            }
        </style>
    </head>
    <body>
        <!-- Верхняя панель навигации (contextMenuStrip) -->
        <div class="navigation-bar">
            <button id="back-button" class="nav-button" title="Назад">
                <span class="material-icons-round">arrow_back</span>
            </button>
            
            <button id="forward-button" class="nav-button" title="Вперед">
                <span class="material-icons-round">arrow_forward</span>
            </button>
            
            <button id="refresh-button" class="nav-button" title="Обновить">
                <span class="material-icons-round">refresh</span>
            </button>
            
            <div class="url-container">
                <span class="material-icons-round url-icon">public</span>
                <input type="text" id="url-input" class="url-input" placeholder="Введите адрес или поисковый запрос">
            </div>
            
            <button id="bookmarks-button" class="nav-button" title="Закладки">
                <span class="material-icons-round">bookmark</span>
            </button>
            
            <button id="menu-button" class="nav-button" title="Меню">
                <span class="material-icons-round">more_vert</span>
            </button>
        </div>
        
        <!-- Панель вкладок -->
        <div class="tabs-container" id="tabs-container">
            <!-- Вкладки будут добавлены через JavaScript -->
            <button class="new-tab-btn" id="new-tab-button">
                <span class="material-icons-round">add</span>
            </button>
        </div>
        
        <!-- Основной контент -->
        <div class="content-area" id="content-area">
            <!-- Контент будет загружен через webview -->
        </div>
        
        <!-- Статусная строка -->
        <div class="status-bar">
            <span id="status-text">VLESS VPN активен</span>
            <span id="version-info">Windows 11 Browser v4.0.0</span>
        </div>
        
        <script>
            // === ДОСТУП К ЭЛЕМЕНТАМ ИНТЕРФЕЙСА ===
            const backButton = document.getElementById('back-button');
            const forwardButton = document.getElementById('forward-button');
            const refreshButton = document.getElementById('refresh-button');
            const urlInput = document.getElementById('url-input');
            const bookmarksButton = document.getElementById('bookmarks-button');
            const menuButton = document.getElementById('menu-button');
            const tabsContainer = document.getElementById('tabs-container');
            const newTabButton = document.getElementById('new-tab-button');
            const contentArea = document.getElementById('content-area');
            const statusText = document.getElementById('status-text');
            
            // === ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ===
            let currentTabs = [];
            
            // === ФУНКЦИИ НАВИГАЦИИ ===
            function navigate() {
                const url = urlInput.value;
                if (url) {
                    pywebview.api.navigate(url);
                    statusText.textContent = `Загрузка: ${url}`;
                }
            }
            
            function goBack() {
                pywebview.api.go_back();
                // URL будет обновлен автоматически в API
            }
            
            function goForward() {
                pywebview.api.go_forward();
                // URL будет обновлен автоматически в API
            }
            
            function refresh() {
                pywebview.api.refresh();
                statusText.textContent = 'Обновление страницы...';
            }
            
            function getCurrentUrl() {
                pywebview.api.get_current_url().then(response => {
                    if (response.success && response.url) {
                        urlInput.value = response.url;
                    }
                });
            }
            
            // === ФУНКЦИИ ДЛЯ ВКЛАДОК ===
            function createNewTab() {
                pywebview.api.create_new_tab().then(response => {
                    if (response.success) {
                        refreshTabs();
                    }
                });
            }
            
            function switchTab(tabId) {
                pywebview.api.switch_tab(tabId).then(response => {
                    if (response.success) {
                        refreshTabs();
                    }
                });
            }
            
            function closeTab(event, tabId) {
                event.stopPropagation(); // Предотвращаем переключение вкладки
                pywebview.api.close_tab(tabId).then(response => {
                    if (response.success) {
                        refreshTabs();
                    }
                });
            }
            
            function refreshTabs() {
                pywebview.api.get_tabs().then(tabs => {
                    currentTabs = tabs;
                    renderTabs();
                    
                    // Обновляем URL в адресной строке
                    const activeTab = currentTabs.find(tab => tab.is_active);
                    if (activeTab) {
                        urlInput.value = activeTab.url;
                    }
                });
            }
            
            function renderTabs() {
                // Очищаем все вкладки, кроме кнопки новой вкладки
                while (tabsContainer.firstChild && tabsContainer.firstChild !== newTabButton) {
                    tabsContainer.removeChild(tabsContainer.firstChild);
                }
                
                // Добавляем вкладки в порядке их создания
                currentTabs.forEach(tab => {
                    const tabElement = document.createElement('div');
                    tabElement.className = `tab ${tab.is_active ? 'active' : ''}`;
                    tabElement.onclick = () => switchTab(tab.id);
                    
                    const tabIcon = document.createElement('span');
                    tabIcon.className = 'material-icons-round tab-icon';
                    tabIcon.textContent = 'web';
                    
                    const tabTitle = document.createElement('div');
                    tabTitle.className = 'tab-title';
                    tabTitle.textContent = tab.title || 'Новая вкладка';
                    
                    const closeButton = document.createElement('div');
                    closeButton.className = 'tab-close';
                    closeButton.innerHTML = '<span class="material-icons-round" style="font-size: 14px;">close</span>';
                    closeButton.onclick = (e) => closeTab(e, tab.id);
                    
                    tabElement.appendChild(tabIcon);
                    tabElement.appendChild(tabTitle);
                    tabElement.appendChild(closeButton);
                    
                    tabsContainer.insertBefore(tabElement, newTabButton);
                });
            }
            
            // === ОБРАБОТЧИКИ СОБЫТИЙ ===
            backButton.addEventListener('click', goBack);
            forwardButton.addEventListener('click', goForward);
            refreshButton.addEventListener('click', refresh);
            newTabButton.addEventListener('click', createNewTab);
            
            urlInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    navigate();
                }
            });
            
            // === ГОРЯЧИЕ КЛАВИШИ ===
            document.addEventListener('keydown', function(e) {
                if (e.ctrlKey) {
                    switch(e.key) {
                        case 't':
                            e.preventDefault();
                            createNewTab();
                            break;
                        case 'r':
                            e.preventDefault();
                            refresh();
                            break;
                        case 'l':
                            e.preventDefault();
                            urlInput.focus();
                            urlInput.select();
                            break;
                    }
                }
            });
            
            // === ИНИЦИАЛИЗАЦИЯ ===
            window.addEventListener('pywebviewready', function() {
                console.log('PyWebview API готов');
                refreshTabs();
                getCurrentUrl();
            });
            
            // Начальная инициализация интерфейса
            setTimeout(() => {
                refreshTabs();
                statusText.textContent = '✅ Браузер готов • VLESS VPN активен';
            }, 500);
        </script>
    </body>
    </html>
    """
    
    # Создаём API объект
    browser_logger.info("Создание Win11BrowserApi...")
    api = Win11BrowserApi()
    
    # Создаём окно
    browser_logger.info("Создание Windows 11 webview окна...")
    window = webview.create_window(
        'Windows 11 Browser с VLESS VPN', 
        html,
        width=1400,
        height=900,
        min_size=(1000, 700),
        resizable=True,
        js_api=api
    )
    
    # Связываем API с окном
    api.set_window(window)
    browser_logger.info("API связан с окном webview")
    
    browser_logger.info("🚀 Запуск Windows 11 браузера...")
    
    try:
        # Запускаем webview без параметра api (совместимо с pywebview 3.x, 4.x и 5.x)
        browser_logger.debug("Запуск webview с универсальным методом")
        # API объект уже передан в create_window, дополнительно передавать не нужно
        webview.start(debug=False, http_server=True)
        browser_logger.info("✅ Windows 11 браузер успешно запущен")
    except Exception as e:
        log_exception(browser_logger, e, "webview.start")
        raise


if __name__ == '__main__':
    start()
