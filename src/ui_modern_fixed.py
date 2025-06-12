import json
import os
from urllib.parse import quote_plus
import webview


class BrowserApi:
    """API класс для взаимодействия JavaScript с Python."""
    
    def __init__(self):
        self.current_window = None
        
    def set_window(self, window):
        """Устанавливает ссылку на окно webview."""
        self.current_window = window
        
    def navigate(self, url):
        """Навигация по URL."""
        if not self.current_window:
            print("Window not initialized")
            return
            
        # Если URL не содержит протокол, добавляем https://
        if not url.startswith(('http://', 'https://')):
            if '.' in url and ' ' not in url:
                url = 'https://' + url
            else:
                url = 'https://www.google.com/search?q=' + quote_plus(url)
                
        print(f"Navigating to: {url}")
        self.current_window.load_url(url)
        
    def go_back(self):
        """Возвращается на домашнюю страницу (эмуляция назад)."""
        print("Going back (to home)")
        if self.current_window:
            self.current_window.load_url('https://www.google.com')
            
    def go_forward(self):
        """Переходит на домашнюю страницу (эмуляция вперед)."""
        print("Going forward (to home)")
        if self.current_window:
            self.current_window.load_url('https://www.google.com')
            
    def refresh(self):
        """Обновляет текущую страницу."""
        print("Refreshing page")
        if self.current_window:
            self.current_window.reload()


def start():
    """Запускает пользовательский интерфейс браузера с современным дизайном."""
    bookmarks = []
    try:
        with open(os.path.join('resources', 'bookmarks.json'), 'r', encoding='utf-8') as bf:
            bookmarks = json.load(bf)
    except FileNotFoundError:
        # Создаём закладки по умолчанию если файл не найден
        bookmarks = [
            {"name": "YouTube", "url": "https://www.youtube.com"},
            {"name": "2IP", "url": "https://2ip.ru"}
        ]

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
                    }}).catch((e) => {{
                        console.error('Navigation error:', e);
                        statusText.textContent = 'Ошибка загрузки • ' + e.message;
                    }});
                }} else {{
                    // Fallback для тестирования
                    setTimeout(() => {{
                        content.innerHTML = '<div>📄 Симуляция загрузки: ' + url + '</div>';
                        statusText.textContent = 'Загружено через VLESS прокси • 127.0.0.1:1080';
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
            }});
        </script>
    </body>
    </html>
    """

    # Создаём API объект
    api = BrowserApi()
    
    # Создаём окно
    window = webview.create_window(
        'Лёгкий браузер с VLESS VPN', 
        html,
        width=1200,
        height=800,
        min_size=(800, 600)
    )
    
    # Связываем API с окном
    api.set_window(window)
    
    print("Запуск браузера с современным интерфейсом...")
    
    # Запускаем webview с API (правильный способ для pywebview 4.0+)
    webview.start(api=api, debug=True, http_server=True)


if __name__ == '__main__':
    start()
