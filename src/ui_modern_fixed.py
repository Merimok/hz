import json
import os
from urllib.parse import quote_plus
import webview
from src.core.tab_manager import TabManager
from src.logger import browser_logger, log_exception


class BrowserApi:
    """API класс для взаимодействия JavaScript с Python с поддержкой вкладок."""
    
    def __init__(self):
        self.current_window = None
        self.tab_manager = TabManager()
        
        # Создаем первую вкладку по умолчанию
        self.tab_manager.create_tab("https://www.google.com", "Google")
        
    def set_window(self, window):
        """Устанавливает ссылку на окно webview."""
        self.current_window = window
        
    def navigate(self, url):
        """Навигация по URL в активной вкладке."""
        if not self.current_window:
            print("Window not initialized")
            return
            
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
            active_tab.title = url  # Временно, потом можно получить настоящий title
                
        print(f"Navigating to: {url}")
        self.current_window.load_url(url)
        
    def go_back(self):
        """Возвращается на домашнюю страницу (эмуляция назад)."""
        print("Going back (to home)")
        if self.current_window:
            self.navigate('https://www.google.com')
            
    def go_forward(self):
        """Переходит на домашнюю страницу (эмуляция вперед)."""
        print("Going forward (to home)")
        if self.current_window:
            self.navigate('https://www.google.com')
            
    def refresh(self):
        """Обновляет текущую страницу."""
        print("Refreshing page")
        if self.current_window:
            self.current_window.reload()
    
    # Новые методы для работы с вкладками
    def create_new_tab(self, url="https://www.google.com"):
        """Создает новую вкладку."""
        tab = self.tab_manager.create_tab(url, "Новая вкладка")
        print(f"Created new tab: {tab.id}")
        return {
            'id': tab.id,
            'url': tab.url,
            'title': tab.title,
            'is_pinned': tab.is_pinned
        }
    
    def close_tab(self, tab_id):
        """Закрывает вкладку."""
        result = self.tab_manager.close_tab(tab_id)
        if result and self.current_window:
            # Если закрыли активную вкладку, переключаемся на другую
            active_tab = self.tab_manager.get_active_tab()
            if active_tab:
                self.current_window.load_url(active_tab.url)
        return result
    
    def switch_tab(self, tab_id):
        """Переключается на вкладку."""
        result = self.tab_manager.switch_tab(tab_id)
        if result and self.current_window:
            active_tab = self.tab_manager.get_active_tab()
            if active_tab:
                self.current_window.load_url(active_tab.url)
        return result
    
    def get_all_tabs(self):
        """Возвращает список всех вкладок."""
        tabs = []
        for tab in self.tab_manager.tabs:
            tabs.append({
                'id': tab.id,
                'url': tab.url,
                'title': tab.title,
                'is_pinned': tab.is_pinned,
                'is_active': tab.id == self.tab_manager.active_tab_id
            })
        return tabs
    
    def pin_tab(self, tab_id):
        """Закрепляет/открепляет вкладку."""
        return self.tab_manager.pin_tab(tab_id)
    
    def move_tab(self, tab_id, new_index):
        """Перемещает вкладку на новую позицию."""
        return self.tab_manager.move_tab(tab_id, new_index)


def start():
    """Запускает пользовательский интерфейс браузера с современным дизайном."""
    browser_logger.info("Запуск UI с поддержкой вкладок...")
    
    bookmarks = []
    try:
        with open(os.path.join('resources', 'bookmarks.json'), 'r', encoding='utf-8') as bf:
            bookmarks = json.load(bf)
        browser_logger.info(f"Загружено {len(bookmarks)} закладок")
    except FileNotFoundError:
        # Создаём закладки по умолчанию если файл не найден
        bookmarks = [
            {"name": "YouTube", "url": "https://www.youtube.com"},
            {"name": "2IP", "url": "https://2ip.ru"}
        ]
        browser_logger.warning("Файл закладок не найден, используются закладки по умолчанию")

    start_url = 'https://www.google.com'
    
    # Современный HTML дизайн
    html = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Лёгкий браузер с VLESS VPN</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                height: 100vh;
                overflow: hidden;
            }}
            
            .browser-container {{
                display: flex;
                flex-direction: column;
                height: 100vh;
                background: white;
                box-shadow: 0 0 30px rgba(0,0,0,0.2);
            }}
            
            .toolbar {{
                background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                padding: 12px 16px;
                display: flex;
                align-items: center;
                gap: 12px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                position: relative;
            }}
            
            .nav-btn {{
                background: rgba(255,255,255,0.2);
                border: none;
                border-radius: 8px;
                color: white;
                width: 40px;
                height: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: all 0.2s ease;
                font-size: 16px;
                backdrop-filter: blur(10px);
            }}
            
            .nav-btn:hover {{
                background: rgba(255,255,255,0.3);
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            }}
            
            .address-bar {{
                flex: 1;
                height: 40px;
                border: none;
                border-radius: 20px;
                padding: 0 20px;
                font-size: 14px;
                background: rgba(255,255,255,0.95);
                backdrop-filter: blur(10px);
                box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
                transition: all 0.2s ease;
            }}
            
            .address-bar:focus {{
                outline: none;
                background: white;
                box-shadow: 0 0 0 3px rgba(255,255,255,0.3), inset 0 2px 4px rgba(0,0,0,0.1);
            }}
            
            .go-btn {{
                background: rgba(255,255,255,0.2);
                border: none;
                border-radius: 8px;
                color: white;
                padding: 8px 16px;
                cursor: pointer;
                transition: all 0.2s ease;
                font-weight: 500;
                backdrop-filter: blur(10px);
            }}
            
            .go-btn:hover {{
                background: rgba(255,255,255,0.3);
                transform: translateY(-1px);
            }}
            
            .bookmarks {{
                background: rgba(255,255,255,0.2);
                border: none;
                border-radius: 8px;
                color: white;
                padding: 8px 12px;
                cursor: pointer;
                font-size: 14px;
                backdrop-filter: blur(10px);
                transition: all 0.2s ease;
            }}
            
            .webview-container {{
                flex: 1;
                position: relative;
                overflow: hidden;
                background: #f8fafc;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                color: #64748b;
            }}
            
            .status-bar {{
                background: #f1f5f9;
                padding: 8px 16px;
                font-size: 12px;
                color: #64748b;
                border-top: 1px solid #e2e8f0;
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            
            .vpn-status {{
                background: #10b981;
                color: white;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: 500;
                display: flex;
                align-items: center;
                gap: 4px;
            }}
            
            .vpn-status::before {{
                content: '🔒';
                font-size: 10px;
            }}
            
            .home-btn {{
                background: rgba(255,255,255,0.2);
                border: none;
                border-radius: 8px;
                color: white;
                width: 40px;
                height: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: all 0.2s ease;
                backdrop-filter: blur(10px);
                font-size: 18px;
            }}
            
            .home-btn:hover {{
                background: rgba(255,255,255,0.3);
                transform: translateY(-1px);
            }}
            
            /* Стили для панели вкладок */
            .tabs-container {{
                background: #f8fafc;
                border-bottom: 1px solid #e2e8f0;
                display: flex;
                align-items: center;
                padding: 0 8px;
                gap: 4px;
                overflow-x: auto;
                min-height: 40px;
            }}
            
            .tab {{
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px 8px 0 0;
                padding: 8px 12px;
                display: flex;
                align-items: center;
                gap: 8px;
                cursor: pointer;
                transition: all 0.2s ease;
                min-width: 120px;
                max-width: 200px;
                position: relative;
                user-select: none;
            }}
            
            .tab:hover {{
                background: #f1f5f9;
                border-color: #cbd5e1;
            }}
            
            .tab.active {{
                background: #6366f1;
                color: white;
                border-color: #6366f1;
                box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
            }}
            
            .tab.pinned {{
                min-width: 40px;
                padding: 8px;
                border-radius: 8px;
            }}
            
            .tab-title {{
                flex: 1;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                font-size: 13px;
            }}
            
            .tab-close {{
                background: rgba(0,0,0,0.1);
                border: none;
                border-radius: 4px;
                color: inherit;
                width: 20px;
                height: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                opacity: 0.7;
                transition: all 0.2s ease;
                font-size: 12px;
            }}
            
            .tab-close:hover {{
                background: rgba(0,0,0,0.2);
                opacity: 1;
            }}
            
            .tab.active .tab-close {{
                background: rgba(255,255,255,0.2);
            }}
            
            .tab.active .tab-close:hover {{
                background: rgba(255,255,255,0.3);
            }}
            
            .new-tab-btn {{
                background: #f1f5f9;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                color: #64748b;
                width: 32px;
                height: 32px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: all 0.2s ease;
                font-size: 16px;
                margin-left: 4px;
            }}
            
            .new-tab-btn:hover {{
                background: #e2e8f0;
                color: #475569;
            }}
        </style>
    </head>
    <body>
        <div class="browser-container">
            <div class="toolbar">
                <button class="nav-btn" onclick="goBack()" title="Назад">←</button>
                <button class="nav-btn" onclick="goForward()" title="Вперёд">→</button>
                <button class="nav-btn" onclick="refresh()" title="Обновить">↻</button>
                <button class="home-btn" onclick="goHome()" title="Домой">🏠</button>
                
                <input class="address-bar" id="addressBar" value="{start_url}" placeholder="Введите URL или поисковый запрос...">
                
                <button class="go-btn" onclick="navigate()">Перейти</button>
                
                <select class="bookmarks" onchange="navigateToBookmark(this.value)">
                    <option value="">Закладки</option>"""
    
    # Добавляем закладки
    for bookmark in bookmarks:
        html += f'<option value="{bookmark["url"]}">{bookmark["name"]}</option>'
    
    html += f"""
                </select>
            </div>
            
            <!-- Панель вкладок -->
            <div class="tabs-container" id="tabsContainer">
                <button class="new-tab-btn" onclick="createNewTab()" title="Новая вкладка">+</button>
            </div>
            
            <div class="webview-container" id="content">
                <div>🌐 Введите URL в адресную строку для навигации</div>
            </div>
            
            <div class="status-bar">
                <div class="vpn-status">VPN Активен</div>
                <span id="statusText">Подключено через VLESS прокси • 127.0.0.1:1080</span>
            </div>
        </div>

        <script>
            const addressBar = document.getElementById('addressBar');
            const statusText = document.getElementById('statusText');
            const content = document.getElementById('content');
            
            function navigate(customUrl) {{
                const url = customUrl || addressBar.value.trim();
                if (!url) return;
                
                statusText.textContent = 'Загрузка... • ' + url;
                content.innerHTML = '<div>🔄 Загрузка: ' + url + '</div>';
                
                // Используем pywebview API
                if (window.pywebview && window.pywebview.api) {{
                    window.pywebview.api.navigate(url).then(() => {{
                        statusText.textContent = 'Загружено через VLESS прокси • 127.0.0.1:1080';
                        // Обновляем заголовок активной вкладки
                        updateActiveTabTitle(url);
                    }}).catch((e) => {{
                        console.error('Navigation error:', e);
                        statusText.textContent = 'Ошибка загрузки • ' + e.message;
                    }});
                }} else {{
                    // Fallback для тестирования
                    setTimeout(() => {{
                        content.innerHTML = '<div>📄 Симуляция загрузки: ' + url + '</div>';
                        statusText.textContent = 'Загружено через VLESS прокси • 127.0.0.1:1080';
                        // Обновляем заголовок активной вкладки
                        updateActiveTabTitle(url);
                    }}, 1000);
                }}
                
                addressBar.value = url;
            }}
            
            function goBack() {{
                if (window.pywebview && window.pywebview.api) {{
                    window.pywebview.api.go_back();
                }} else {{
                    navigate('https://www.google.com');
                }}
            }}
            
            function goForward() {{
                if (window.pywebview && window.pywebview.api) {{
                    window.pywebview.api.go_forward();
                }} else {{
                    navigate('https://www.google.com');
                }}
            }}
            
            function refresh() {{
                if (window.pywebview && window.pywebview.api) {{
                    window.pywebview.api.refresh();
                }} else {{
                    window.location.reload();
                }}
            }}
            
            function goHome() {{
                navigate('{start_url}');
            }}
            
            function navigateToBookmark(url) {{
                if (url) {{
                    navigate(url);
                }}
                event.target.selectedIndex = 0;
            }}
            
            // Обработка Enter в адресной строке
            addressBar.addEventListener('keypress', function(e) {{
                if (e.key === 'Enter') {{
                    navigate();
                }}
            }});
            
            // Инициализация при загрузке
            window.addEventListener('pywebviewready', function() {{
                console.log('PyWebview API готов');
                statusText.textContent = 'Готов к работе через VLESS прокси • 127.0.0.1:1080';
                loadTabs(); // Загружаем список вкладок
            }});
            
            // === ФУНКЦИИ ДЛЯ РАБОТЫ С ВКЛАДКАМИ ===
            
            function createNewTab() {{
                if (window.pywebview && window.pywebview.api) {{
                    window.pywebview.api.create_new_tab().then(function(tab) {{
                        addTabToUI(tab);
                        switchToTab(tab.id);
                    }}).catch(function(e) {{
                        console.error('Ошибка создания вкладки:', e);
                    }});
                }} else {{
                    // Fallback режим
                    console.log('Создание новой вкладки (fallback режим)');
                }}
            }}
            
            function closeTab(event, tabId) {{
                event.stopPropagation(); // Предотвращаем переключение на вкладку
                
                if (window.pywebview && window.pywebview.api) {{
                    window.pywebview.api.close_tab(tabId).then(function(result) {{
                        if (result) {{
                            removeTabFromUI(tabId);
                        }}
                    }}).catch(function(e) {{
                        console.error('Ошибка закрытия вкладки:', e);
                    }});
                }} else {{
                    // Fallback режим
                    removeTabFromUI(tabId);
                }}
            }}
            
            function switchToTab(tabId) {{
                if (window.pywebview && window.pywebview.api) {{
                    window.pywebview.api.switch_tab(tabId).then(function(result) {{
                        if (result) {{
                            updateActiveTab(tabId);
                        }}
                    }}).catch(function(e) {{
                        console.error('Ошибка переключения вкладки:', e);
                    }});
                }} else {{
                    // Fallback режим
                    updateActiveTab(tabId);
                }}
            }}
            
            function loadTabs() {{
                if (window.pywebview && window.pywebview.api) {{
                    window.pywebview.api.get_all_tabs().then(function(tabs) {{
                        renderTabs(tabs);
                    }}).catch(function(e) {{
                        console.error('Ошибка загрузки вкладок:', e);
                    }});
                }}
            }}
            
            function renderTabs(tabs) {{
                const tabsContainer = document.getElementById('tabsContainer');
                const newTabBtn = tabsContainer.querySelector('.new-tab-btn');
                
                // Очищаем существующие вкладки (кроме кнопки "+")
                tabsContainer.querySelectorAll('.tab').forEach(tab => tab.remove());
                
                // Добавляем все вкладки
                tabs.forEach(function(tab) {{
                    addTabToUI(tab, newTabBtn);
                }});
            }}
            
            function addTabToUI(tab, beforeElement) {{
                const tabsContainer = document.getElementById('tabsContainer');
                const newTabBtn = beforeElement || tabsContainer.querySelector('.new-tab-btn');
                
                const tabElement = document.createElement('div');
                tabElement.className = 'tab' + (tab.is_active ? ' active' : '') + (tab.is_pinned ? ' pinned' : '');
                tabElement.setAttribute('data-tab-id', tab.id);
                tabElement.onclick = () => switchToTab(tab.id);
                
                const title = tab.title.length > 20 ? tab.title.substring(0, 20) + '...' : tab.title;
                
                tabElement.innerHTML = `
                    <span class="tab-title">${{title}}</span>
                    <button class="tab-close" onclick="closeTab(event, '${{tab.id}}')" title="Закрыть вкладку">×</button>
                `;
                
                tabsContainer.insertBefore(tabElement, newTabBtn);
            }}
            
            function removeTabFromUI(tabId) {{
                const tabElement = document.querySelector(`[data-tab-id="${{tabId}}"]`);
                if (tabElement) {{
                    tabElement.remove();
                }}
            }}
            
            function updateActiveTab(tabId) {{
                // Убираем активность со всех вкладок
                document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
                
                // Добавляем активность к выбранной вкладке
                const activeTab = document.querySelector(`[data-tab-id="${{tabId}}"]`);
                if (activeTab) {{
                    activeTab.classList.add('active');
                }}
            }}
            
            // Обновление заголовка активной вкладки при навигации
            function updateActiveTabTitle(title) {{
                const activeTab = document.querySelector('.tab.active .tab-title');
                if (activeTab) {{
                    const shortTitle = title.length > 20 ? title.substring(0, 20) + '...' : title;
                    activeTab.textContent = shortTitle;
                }}
            }}
        </script>
    </body>
    </html>
    """

    # Создаём API объект
    browser_logger.info("Создание BrowserApi с TabManager...")
    api = BrowserApi()
    
    # Создаём окно
    browser_logger.info("Создание webview окна...")
    window = webview.create_window(
        'Лёгкий браузер с VLESS VPN', 
        html,
        width=1200,
        height=800,
        min_size=(800, 600),
        js_api=api  # Передаем API для старых версий
    )
    
    # Связываем API с окном
    api.set_window(window)
    browser_logger.info("API связан с окном webview")
    
    browser_logger.info("Запуск браузера с современным интерфейсом...")
    
    try:
        # Проверяем версию pywebview для обратной совместимости
        import inspect
        start_signature = inspect.signature(webview.start)
        if 'api' in start_signature.parameters:
            # Новая версия pywebview (4.0+)
            browser_logger.debug("Используем новый API pywebview 4.0+")
            webview.start(api=api, debug=True, http_server=True)
        else:
            # Старая версия pywebview (3.x)
            browser_logger.debug("Используем legacy API pywebview 3.x")
            webview.start(debug=True, http_server=True)
        browser_logger.info("Браузер успешно запущен")
    except Exception as e:
        log_exception(browser_logger, e, "webview.start")
        raise


if __name__ == '__main__':
    start()
