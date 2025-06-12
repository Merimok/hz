import json
import os
from urllib.parse import quote_plus
import webview
from src.base_api import BaseBrowserApi, create_webview_window_safe, start_webview_safe, load_bookmarks, COMMON_CSS_VARIABLES


class BasicBrowserApi(BaseBrowserApi):
    """Базовый API для простого интерфейса."""
    pass


def start():
    """Запускает пользовательский интерфейс браузера с закладками."""
    
    # Загружаем закладки
    bookmarks = load_bookmarks()
    start_url = 'https://www.google.com'
    
    # Генерируем опции для закладок
    options = ''.join([f"<option value='{b['url']}'>{b['name']}</option>" for b in bookmarks])

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Lightweight Browser</title>
        <style>
            {COMMON_CSS_VARIABLES}
            
            body {{
                margin: 0;
                padding: 0;
                font-family: var(--font-family);
                background: var(--bg-color);
            }}
            
            .toolbar {{
                display: flex;
                padding: 10px;
                background: var(--secondary-color);
                border-bottom: 1px solid var(--border-color);
                gap: 8px;
                align-items: center;
            }}
            
            .nav-btn {{
                background: var(--primary-color);
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: var(--border-radius);
                cursor: pointer;
                font-size: 16px;
                transition: background 0.2s;
            }}
            
            .nav-btn:hover {{
                background: var(--primary-hover);
            }}
            
            #address {{
                flex: 1;
                padding: 8px 12px;
                border: 1px solid var(--border-color);
                border-radius: var(--border-radius);
                font-size: 14px;
                outline: none;
            }}
            
            #address:focus {{
                border-color: var(--primary-color);
                box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1);
            }}
            
            .bookmarks-select {{
                padding: 8px;
                border: 1px solid var(--border-color);
                border-radius: var(--border-radius);
                background: white;
                cursor: pointer;
            }}
            
            .webview {{
                width: 100%;
                height: calc(100vh - 60px);
                border: none;
            }}
        </style>
    </head>
    <body>
        <div class="toolbar">
            <button class="nav-btn" onclick="goBack()" title="Назад">←</button>
            <button class="nav-btn" onclick="goForward()" title="Вперёд">→</button>
            <button class="nav-btn" onclick="refresh()" title="Обновить">↻</button>
            <input id='address' value='{start_url}' placeholder="Введите URL или поисковый запрос..." />
            <button class="nav-btn" onclick="navigate()">Перейти</button>
            <select class="bookmarks-select" onchange="navigateToBookmark(this.value)">
                <option value="">Закладки</option>
                {options}
            </select>
        </div>
        <webview id='wv' src='{start_url}' class="webview"></webview>
        
        <script>
            const addressBar = document.getElementById('address');
            
            // Обработка Enter в адресной строке
            addressBar.addEventListener('keypress', function(e) {{
                if (e.key === 'Enter') {{
                    navigate();
                }}
            }});
            
            // Горячие клавиши
            document.addEventListener('keydown', function(e) {{
                if (e.ctrlKey) {{
                    switch(e.key) {{
                        case 'l':
                        case 'L':
                            e.preventDefault();
                            addressBar.focus();
                            addressBar.select();
                            break;
                        case 'r':
                        case 'R':
                            e.preventDefault();
                            refresh();
                            break;
                    }}
                }}
                
                if (e.key === 'F5') {{
                    e.preventDefault();
                    refresh();
                }}
            }});
            
            function navigate(customUrl) {{
                const url = customUrl || addressBar.value.trim();
                if (!url) return;
                
                if (window.pywebview && window.pywebview.api) {{
                    window.pywebview.api.navigate(url);
                    addressBar.value = url;
                }}
            }}
            
            function goBack() {{
                if (window.pywebview && window.pywebview.api) {{
                    window.pywebview.api.go_back();
                }}
            }}
            
            function goForward() {{
                if (window.pywebview && window.pywebview.api) {{
                    window.pywebview.api.go_forward();
                }}
            }}
            
            function refresh() {{
                if (window.pywebview && window.pywebview.api) {{
                    window.pywebview.api.refresh();
                }}
            }}
            
            function navigateToBookmark(url) {{
                if (url) {{
                    navigate(url);
                    // Сбрасываем выбор
                    event.target.selectedIndex = 0;
                }}
            }}
        </script>
    </body>
    </html>
    """

    # Создаём API объект
    api = BasicBrowserApi()
    
    # Создаём окно безопасно
    window, supports_api_param = create_webview_window_safe(
        'Lightweight Browser with VLESS VPN', 
        html, 
        api,
        width=1200,
        height=800,
        min_size=(800, 600)
    )

    # Запускаем webview безопасно
    start_webview_safe(api, supports_api_param)
