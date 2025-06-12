import json
import os
from urllib.parse import quote_plus
import webview
from src.core.tab_manager import TabManager
from src.logger import browser_logger, log_exception


class ModernBrowserApi:
    """Современный API для браузера с продвинутым TabManager."""
    
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
        return {'success': True, 'url': url}
        
    def go_back(self):
        """История назад (эмуляция)."""
        browser_logger.info("История назад")
        return self.navigate('https://www.google.com')
            
    def go_forward(self):
        """История вперед (эмуляция)."""
        browser_logger.info("История вперед")
        return self.navigate('https://www.google.com')
            
    def refresh(self):
        """Обновляет текущую страницу."""
        browser_logger.info("Обновление страницы")
        if self.current_window:
            self.current_window.reload()
        return {'success': True}
    
    # === МЕТОДЫ ДЛЯ РАБОТЫ С ВКЛАДКАМИ ===
    
    def create_new_tab(self, url="https://www.google.com"):
        """Создает новую вкладку."""
        domain = url.split('/')[2] if '://' in url else "Новая вкладка"
        tab = self.tab_manager.create_tab(url, f"🌐 {domain}")
        browser_logger.info(f"Создана вкладка: {tab.id}")
        
        # Переключаемся на новую вкладку
        self.switch_tab(tab.id)
        
        return {
            'success': True,
            'tab': {
                'id': tab.id,
                'url': tab.url,
                'title': tab.title,
                'is_pinned': tab.is_pinned
            }
        }
    
    def close_tab(self, tab_id):
        """Закрывает вкладку."""
        result = self.tab_manager.close_tab(tab_id)
        if result and self.current_window:
            # Если закрыли активную вкладку, переключаемся на другую
            active_tab = self.tab_manager.get_active_tab()
            if active_tab:
                self.current_window.load_url(active_tab.url)
        
        browser_logger.info(f"Закрыта вкладка: {tab_id}")
        return {'success': result, 'tabs': self.get_all_tabs()}
    
    def switch_tab(self, tab_id):
        """Переключается на вкладку."""
        result = self.tab_manager.switch_tab(tab_id)
        if result and self.current_window:
            active_tab = self.tab_manager.get_active_tab()
            if active_tab:
                self.current_window.load_url(active_tab.url)
                browser_logger.info(f"Переключение на вкладку: {active_tab.title}")
        
        return {'success': result, 'active_tab_id': tab_id}
    
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
        result = self.tab_manager.pin_tab(tab_id)
        browser_logger.info(f"Закрепление вкладки {tab_id}: {result}")
        return {'success': result, 'tabs': self.get_all_tabs()}


def start():
    """Запускает современный браузер с Material Design 3."""
    browser_logger.info("🚀 Запуск СОВРЕМЕННОГО браузера с TabManager...")
    
    # Загрузка закладок
    bookmarks = []
    try:
        with open(os.path.join('resources', 'bookmarks.json'), 'r', encoding='utf-8') as bf:
            bookmarks = json.load(bf)
        browser_logger.info(f"Загружено {len(bookmarks)} закладок")
    except FileNotFoundError:
        bookmarks = [
            {"name": "🎬 YouTube", "url": "https://www.youtube.com"},
            {"name": "🔍 2IP", "url": "https://2ip.ru"},
            {"name": "📰 Habr", "url": "https://habr.com"},
            {"name": "🛒 Amazon", "url": "https://amazon.com"}
        ]
        browser_logger.warning("Файл закладок не найден, используются закладки по умолчанию")

    start_url = 'https://www.google.com'
    
    # === СОВРЕМЕННЫЙ MATERIAL DESIGN 3 HTML ===
    html = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🚀 Современный браузер | VLESS VPN</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <link href="https://fonts.googleapis.com/icon?family=Material+Icons+Round" rel="stylesheet">
        <style>
            :root {{
                --primary: #6366f1;
                --primary-light: #818cf8;
                --primary-dark: #4f46e5;
                --surface: #ffffff;
                --surface-variant: #f8fafc;
                --surface-container: #f1f5f9;
                --on-surface: #1e293b;
                --on-surface-variant: #64748b;
                --outline: #cbd5e1;
                --outline-variant: #e2e8f0;
                --error: #ef4444;
                --success: #10b981;
                --warning: #f59e0b;
                --shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
                --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
                --border-radius: 12px;
                --border-radius-sm: 8px;
                --transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            }}
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                height: 100vh;
                overflow: hidden;
                color: var(--on-surface);
            }}
            
            .browser-container {{
                display: flex;
                flex-direction: column;
                height: 100vh;
                background: var(--surface);
                border-radius: var(--border-radius);
                margin: 8px;
                box-shadow: var(--shadow-lg);
                overflow: hidden;
            }}
            
            /* === СОВРЕМЕННАЯ ПАНЕЛЬ ИНСТРУМЕНТОВ === */
            .toolbar {{
                background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
                padding: 16px 20px;
                display: flex;
                align-items: center;
                gap: 12px;
                box-shadow: var(--shadow);
                position: relative;
                z-index: 10;
            }}
            
            .nav-controls {{
                display: flex;
                gap: 8px;
            }}
            
            .nav-btn {{
                background: rgba(255, 255, 255, 0.15);
                border: none;
                border-radius: var(--border-radius-sm);
                color: white;
                width: 40px;
                height: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: var(--transition);
                backdrop-filter: blur(10px);
                position: relative;
                overflow: hidden;
            }}
            
            .nav-btn:hover {{
                background: rgba(255, 255, 255, 0.25);
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }}
            
            .nav-btn:active {{
                transform: translateY(0);
            }}
            
            .nav-btn .material-icons-round {{
                font-size: 20px;
            }}
            
            .address-container {{
                flex: 1;
                position: relative;
                margin: 0 16px;
            }}
            
            .address-bar {{
                width: 100%;
                height: 48px;
                border: none;
                border-radius: 24px;
                padding: 0 24px 0 48px;
                font-size: 15px;
                font-weight: 400;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                transition: var(--transition);
                color: var(--on-surface);
            }}
            
            .address-bar:focus {{
                outline: none;
                background: white;
                box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.5), 0 4px 20px rgba(0, 0, 0, 0.1);
            }}
            
            .address-icon {{
                position: absolute;
                left: 16px;
                top: 50%;
                transform: translateY(-50%);
                color: var(--on-surface-variant);
                font-size: 20px;
            }}
            
            .bookmarks-menu {{
                background: rgba(255, 255, 255, 0.15);
                border: none;
                border-radius: var(--border-radius-sm);
                color: white;
                padding: 10px 16px;
                cursor: pointer;
                transition: var(--transition);
                backdrop-filter: blur(10px);
                font-weight: 500;
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            
            .bookmarks-menu:hover {{
                background: rgba(255, 255, 255, 0.25);
            }}
            
            /* === ПАНЕЛЬ ВКЛАДОК === */
            .tabs-container {{
                background: var(--surface-container);
                border-bottom: 1px solid var(--outline-variant);
                display: flex;
                align-items: center;
                padding: 8px 16px;
                gap: 8px;
                overflow-x: auto;
                min-height: 56px;
                scrollbar-width: none;
                -ms-overflow-style: none;
            }}
            
            .tabs-container::-webkit-scrollbar {{
                display: none;
            }}
            
            .tab {{
                background: var(--surface);
                border: 1px solid var(--outline-variant);
                border-radius: var(--border-radius-sm) var(--border-radius-sm) 0 0;
                padding: 12px 16px;
                display: flex;
                align-items: center;
                gap: 12px;
                cursor: pointer;
                transition: var(--transition);
                min-width: 160px;
                max-width: 240px;
                position: relative;
                user-select: none;
                box-shadow: var(--shadow);
            }}
            
            .tab:hover {{
                background: var(--surface-variant);
                border-color: var(--outline);
                transform: translateY(-1px);
            }}
            
            .tab.active {{
                background: var(--primary);
                color: white;
                border-color: var(--primary);
                box-shadow: 0 4px 20px rgba(99, 102, 241, 0.3);
            }}
            
            .tab.pinned {{
                min-width: 48px;
                max-width: 48px;
                padding: 12px;
                border-radius: var(--border-radius-sm);
            }}
            
            .tab-icon {{
                font-size: 16px;
                opacity: 0.8;
            }}
            
            .tab-title {{
                flex: 1;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                font-size: 14px;
                font-weight: 500;
            }}
            
            .tab-close {{
                background: rgba(0, 0, 0, 0.1);
                border: none;
                border-radius: 50%;
                color: inherit;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                opacity: 0.7;
                transition: var(--transition);
                font-size: 14px;
            }}
            
            .tab-close:hover {{
                background: rgba(0, 0, 0, 0.2);
                opacity: 1;
                transform: scale(1.1);
            }}
            
            .tab.active .tab-close {{
                background: rgba(255, 255, 255, 0.2);
            }}
            
            .tab.active .tab-close:hover {{
                background: rgba(255, 255, 255, 0.3);
            }}
            
            .new-tab-btn {{
                background: var(--surface-variant);
                border: 1px solid var(--outline-variant);
                border-radius: var(--border-radius-sm);
                color: var(--on-surface-variant);
                width: 40px;
                height: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: var(--transition);
                font-size: 20px;
                margin-left: 8px;
            }}
            
            .new-tab-btn:hover {{
                background: var(--outline-variant);
                color: var(--on-surface);
                transform: scale(1.05);
            }}
            
            /* === ОСНОВНАЯ ОБЛАСТЬ === */
            .content-area {{
                flex: 1;
                position: relative;
                background: var(--surface-variant);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                color: var(--on-surface-variant);
                text-align: center;
                padding: 48px 24px;
            }}
            
            .welcome-message {{
                max-width: 600px;
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 24px;
            }}
            
            .welcome-icon {{
                font-size: 64px;
                color: var(--primary);
                opacity: 0.8;
            }}
            
            .welcome-title {{
                font-size: 24px;
                font-weight: 600;
                color: var(--on-surface);
                margin-bottom: 8px;
            }}
            
            .welcome-subtitle {{
                font-size: 16px;
                line-height: 1.5;
                opacity: 0.8;
            }}
            
            /* === СТАТУСНАЯ СТРОКА === */
            .status-bar {{
                background: var(--surface-container);
                padding: 12px 20px;
                font-size: 13px;
                color: var(--on-surface-variant);
                border-top: 1px solid var(--outline-variant);
                display: flex;
                align-items: center;
                gap: 16px;
            }}
            
            .vpn-status {{
                background: var(--success);
                color: white;
                padding: 6px 12px;
                border-radius: 16px;
                font-size: 12px;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 6px;
                box-shadow: var(--shadow);
            }}
            
            .vpn-icon {{
                font-size: 14px;
            }}
            
            .status-text {{
                font-weight: 500;
            }}
            
            /* === АНИМАЦИИ === */
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(10px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            
            @keyframes slideIn {{
                from {{ opacity: 0; transform: translateX(-10px); }}
                to {{ opacity: 1; transform: translateX(0); }}
            }}
            
            .tab {{
                animation: slideIn 0.3s ease;
            }}
            
            .welcome-message {{
                animation: fadeIn 0.5s ease;
            }}
            
            /* === РЕСПОНСИВНОСТЬ === */
            @media (max-width: 768px) {{
                .address-container {{
                    margin: 0 8px;
                }}
                
                .tab {{
                    min-width: 120px;
                    max-width: 180px;
                }}
                
                .tabs-container {{
                    padding: 8px 12px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="browser-container">
            <!-- Панель инструментов -->
            <div class="toolbar">
                <div class="nav-controls">
                    <button class="nav-btn" onclick="goBack()" title="Назад">
                        <span class="material-icons-round">arrow_back</span>
                    </button>
                    <button class="nav-btn" onclick="goForward()" title="Вперёд">
                        <span class="material-icons-round">arrow_forward</span>
                    </button>
                    <button class="nav-btn" onclick="refresh()" title="Обновить">
                        <span class="material-icons-round">refresh</span>
                    </button>
                    <button class="nav-btn" onclick="goHome()" title="Домой">
                        <span class="material-icons-round">home</span>
                    </button>
                </div>
                
                <div class="address-container">
                    <span class="material-icons-round address-icon">search</span>
                    <input class="address-bar" id="addressBar" value="{start_url}" 
                           placeholder="Поиск или введите адрес...">
                </div>
                
                <select class="bookmarks-menu" onchange="navigateToBookmark(this.value)">
                    <option value="">⭐ Закладки</option>"""
    
    # Добавляем закладки
    for bookmark in bookmarks:
        html += f'<option value="{bookmark["url"]}">{bookmark["name"]}</option>'
    
    html += f"""
                </select>
            </div>
            
            <!-- Панель вкладок -->
            <div class="tabs-container" id="tabsContainer">
                <!-- Вкладки будут добавлены динамически -->
            </div>
            
            <!-- Основная область -->
            <div class="content-area" id="contentArea">
                <div class="welcome-message">
                    <span class="material-icons-round welcome-icon">language</span>
                    <div>
                        <div class="welcome-title">🚀 Современный браузер готов!</div>
                        <div class="welcome-subtitle">
                            Введите URL в адресную строку или выберите закладку для начала работы.<br>
                            Поддержка вкладок, VPN и современный дизайн.
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Статусная строка -->
            <div class="status-bar">
                <div class="vpn-status">
                    <span class="material-icons-round vpn-icon">lock</span>
                    VPN Активен
                </div>
                <span class="status-text" id="statusText">Подключено через VLESS прокси • 127.0.0.1:1080</span>
            </div>
        </div>

        <script>
            // === ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ===
            const addressBar = document.getElementById('addressBar');
            const statusText = document.getElementById('statusText');
            const contentArea = document.getElementById('contentArea');
            const tabsContainer = document.getElementById('tabsContainer');
            
            let currentTabs = [];
            let activeTabId = null;
            
            // === API ИНТЕРФЕЙС ===
            const api = window.pywebview?.api || {{
                navigate: (url) => {{ console.log('Navigate:', url); return Promise.resolve({{success: true}}); }},
                go_back: () => {{ console.log('Go back'); return Promise.resolve({{success: true}}); }},
                go_forward: () => {{ console.log('Go forward'); return Promise.resolve({{success: true}}); }},
                refresh: () => {{ console.log('Refresh'); return Promise.resolve({{success: true}}); }},
                create_new_tab: (url) => {{ console.log('New tab:', url); return Promise.resolve({{success: true}}); }},
                close_tab: (id) => {{ console.log('Close tab:', id); return Promise.resolve({{success: true}}); }},
                switch_tab: (id) => {{ console.log('Switch tab:', id); return Promise.resolve({{success: true}}); }},
                get_all_tabs: () => {{ console.log('Get tabs'); return Promise.resolve([]); }},
                pin_tab: (id) => {{ console.log('Pin tab:', id); return Promise.resolve({{success: true}}); }}
            }};
            
            // === НАВИГАЦИЯ ===
            async function navigate(customUrl) {{
                const url = customUrl || addressBar.value.trim();
                if (!url) return;
                
                statusText.textContent = '🔄 Загрузка... • ' + url;
                
                try {{
                    const result = await api.navigate(url);
                    if (result.success) {{
                        statusText.textContent = '✅ Загружено через VLESS прокси • 127.0.0.1:1080';
                        addressBar.value = result.url || url;
                        updateContentArea('Загружается: ' + url);
                    }}
                }} catch (e) {{
                    statusText.textContent = '❌ Ошибка загрузки • ' + e.message;
                }}
            }}
            
            async function goBack() {{
                try {{
                    await api.go_back();
                }} catch (e) {{
                    console.error('Back error:', e);
                }}
            }}
            
            async function goForward() {{
                try {{
                    await api.go_forward();
                }} catch (e) {{
                    console.error('Forward error:', e);
                }}
            }}
            
            async function refresh() {{
                try {{
                    await api.refresh();
                    statusText.textContent = '🔄 Обновление...';
                    setTimeout(() => {{
                        statusText.textContent = '✅ Страница обновлена • VLESS VPN активен';
                    }}, 1000);
                }} catch (e) {{
                    console.error('Refresh error:', e);
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
            
            // === УПРАВЛЕНИЕ ВКЛАДКАМИ ===
            async function createNewTab(url = '{start_url}') {{
                try {{
                    const result = await api.create_new_tab(url);
                    if (result.success) {{
                        await refreshTabs();
                    }}
                }} catch (e) {{
                    console.error('Create tab error:', e);
                }}
            }}
            
            async function closeTab(event, tabId) {{
                event.stopPropagation();
                try {{
                    const result = await api.close_tab(tabId);
                    if (result.success) {{
                        await refreshTabs();
                    }}
                }} catch (e) {{
                    console.error('Close tab error:', e);
                }}
            }}
            
            async function switchToTab(tabId) {{
                try {{
                    const result = await api.switch_tab(tabId);
                    if (result.success) {{
                        await refreshTabs();
                    }}
                }} catch (e) {{
                    console.error('Switch tab error:', e);
                }}
            }}
            
            async function pinTab(event, tabId) {{
                event.stopPropagation();
                try {{
                    const result = await api.pin_tab(tabId);
                    if (result.success) {{
                        await refreshTabs();
                    }}
                }} catch (e) {{
                    console.error('Pin tab error:', e);
                }}
            }}
            
            // === ОБНОВЛЕНИЕ UI ===
            async function refreshTabs() {{
                try {{
                    const tabs = await api.get_all_tabs();
                    currentTabs = tabs;
                    renderTabs();
                }} catch (e) {{
                    console.error('Refresh tabs error:', e);
                }}
            }}
            
            function renderTabs() {{
                tabsContainer.innerHTML = '';
                
                currentTabs.forEach(tab => {{
                    const tabElement = document.createElement('div');
                    tabElement.className = `tab ${{tab.is_active ? 'active' : ''}} ${{tab.is_pinned ? 'pinned' : ''}}`;
                    tabElement.onclick = () => switchToTab(tab.id);
                    
                    const icon = tab.is_pinned ? 
                        '<span class="material-icons-round tab-icon">push_pin</span>' :
                        '<span class="material-icons-round tab-icon">language</span>';
                    
                    const title = tab.is_pinned ? '' : 
                        `<span class="tab-title">${{tab.title}}</span>`;
                    
                    tabElement.innerHTML = `
                        ${{icon}}
                        ${{title}}
                        <button class="tab-close" onclick="closeTab(event, '${{tab.id}}')" title="Закрыть вкладку">
                            <span class="material-icons-round">close</span>
                        </button>
                    `;
                    
                    // Добавляем контекстное меню
                    tabElement.oncontextmenu = (e) => {{
                        e.preventDefault();
                        pinTab(e, tab.id);
                    }};
                    
                    tabsContainer.appendChild(tabElement);
                }});
                
                // Кнопка новой вкладки
                const newTabBtn = document.createElement('button');
                newTabBtn.className = 'new-tab-btn';
                newTabBtn.onclick = createNewTab;
                newTabBtn.title = 'Новая вкладка';
                newTabBtn.innerHTML = '<span class="material-icons-round">add</span>';
                
                tabsContainer.appendChild(newTabBtn);
            }}
            
            function updateContentArea(message) {{
                contentArea.innerHTML = `
                    <div class="welcome-message">
                        <span class="material-icons-round welcome-icon">language</span>
                        <div>
                            <div class="welcome-title">🌐 ${{message}}</div>
                            <div class="welcome-subtitle">Навигация через VLESS VPN активна</div>
                        </div>
                    </div>
                `;
            }}
            
            // === СОБЫТИЯ ===
            addressBar.addEventListener('keypress', function(e) {{
                if (e.key === 'Enter') {{
                    navigate();
                }}
            }});
            
            // Горячие клавиши
            document.addEventListener('keydown', function(e) {{
                if (e.ctrlKey) {{
                    switch(e.key) {{
                        case 't':
                            e.preventDefault();
                            createNewTab();
                            break;
                        case 'w':
                            e.preventDefault();
                            if (currentTabs.length > 1) {{
                                const activeTab = currentTabs.find(t => t.is_active);
                                if (activeTab) closeTab(e, activeTab.id);
                            }}
                            break;
                        case 'r':
                            e.preventDefault();
                            refresh();
                            break;
                    }}
                }}
            }});
            
            // === ИНИЦИАЛИЗАЦИЯ ===
            window.addEventListener('pywebviewready', function() {{
                console.log('🚀 PyWebview API готов');
                refreshTabs();
            }});
            
            // Инициализация при загрузке
            setTimeout(() => {{
                refreshTabs();
                statusText.textContent = '✅ Современный браузер готов • VLESS VPN активен';
            }}, 500);
        </script>
    </body>
    </html>
    """

    # Создаём API объект
    browser_logger.info("Создание ModernBrowserApi...")
    api = ModernBrowserApi()
    
    # Создаём окно
    browser_logger.info("Создание современного webview окна...")
    window = webview.create_window(
        '🚀 Современный браузер | VLESS VPN', 
        html,
        width=1400,
        height=900,
        min_size=(1000, 700),
        resizable=True
    )
    
    # Связываем API с окном
    api.set_window(window)
    browser_logger.info("API связан с окном webview")
    
    browser_logger.info("🎨 Запуск современного браузера с Material Design 3...")
    
    try:
        # Запускаем webview с API
        webview.start(api=api, debug=False, http_server=True)
        browser_logger.info("✅ Современный браузер успешно запущен")
    except Exception as e:
        log_exception(browser_logger, e, "webview.start")
        raise


if __name__ == '__main__':
    start()
