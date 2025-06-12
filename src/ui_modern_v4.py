import json
import os
from urllib.parse import quote_plus
import webview
from src.base_api import BaseBrowserApi, create_webview_window_safe, start_webview_safe, load_bookmarks, COMMON_CSS_VARIABLES


class ModernBrowserApi(BaseBrowserApi):
    """Современный API для интерфейса с градиентом."""
    pass


def start():
    """Запускает пользовательский интерфейс браузера с современным дизайном."""
    
    # Загружаем закладки
    bookmarks = load_bookmarks()
    start_url = 'https://www.google.com'

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Modern Browser</title>
        <style>
            {COMMON_CSS_VARIABLES}
            
            body {{
                margin: 0;
                padding: 0;
                font-family: var(--font-family);
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }}
            
            .browser-container {{
                height: 100vh;
                display: flex;
                flex-direction: column;
                backdrop-filter: blur(10px);
            }}
            
            .toolbar {{
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                border-bottom: 1px solid rgba(255,255,255,0.2);
                padding: 12px 16px;
                display: flex;
                gap: 8px;
                align-items: center;
            }}
            
            .nav-btn {{
                background: rgba(255,255,255,0.2);
                border: none;
                border-radius: var(--border-radius);
                color: white;
                padding: 10px 12px;
                cursor: pointer;
                font-size: 16px;
                backdrop-filter: blur(10px);
                transition: all 0.2s ease;
            }}
            
            .nav-btn:hover {{
                background: rgba(255,255,255,0.3);
                transform: translateY(-1px);
            }}
            
            .address-bar {{
                flex: 1;
                padding: 10px 16px;
                border: none;
                border-radius: 25px;
                background: rgba(255,255,255,0.9);
                font-size: 14px;
                outline: none;
                margin: 0 12px;
            }}
            
            .address-bar:focus {{
                background: white;
                box-shadow: var(--shadow-lg);
            }}
            
            .bookmarks {{
                background: rgba(255,255,255,0.2);
                border: none;
                border-radius: var(--border-radius);
                color: white;
                padding: 8px 12px;
                cursor: pointer;
                font-size: 14px;
                backdrop-filter: blur(10px);
                transition: all 0.2s ease;
            }}
            
            .bookmarks:hover {{
                background: rgba(255,255,255,0.3);
            }}
            
            .webview-container {{
                flex: 1;
                position: relative;
                overflow: hidden;
                background: var(--bg-secondary);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                color: var(--text-light);
            }}
            
            .webview {{
                width: 100%;
                height: 100%;
                border: none;
                background: var(--bg-secondary);
            }}
            
            .status-bar {{
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                padding: 8px 16px;
                font-size: 12px;
                color: white;
                border-top: 1px solid rgba(255,255,255,0.2);
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            
            .vpn-status {{
                background: var(--success-color);
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
                content: "🔒";
            }}
        </style>
    </head>
    <body>
        <div class="browser-container">
            <div class="toolbar">
                <button class="nav-btn" onclick="goBack()" title="Назад">←</button>
                <button class="nav-btn" onclick="goForward()" title="Вперёд">→</button>
                <button class="nav-btn" onclick="refresh()" title="Обновить">↻</button>
                <button class="nav-btn" onclick="goHome()" title="Домой">🏠</button>
                
                <input class="address-bar" id="addressBar" value="{start_url}" placeholder="Введите URL или поисковый запрос...">
                
                <button class="nav-btn" onclick="navigate()">Перейти</button>
                
                <select class="bookmarks" onchange="navigateToBookmark(this.value)">
                    <option value="">Закладки</option>"""
    
    # Добавляем закладки
    for bookmark in bookmarks:
        html += f'<option value="{bookmark["url"]}">{bookmark["name"]}</option>'
    
    html += f"""
                </select>
            </div>
            
            <div class="webview-container">
                <webview id="webview" class="webview" src="{start_url}"></webview>
            </div>
            
            <div class="status-bar">
                <div class="vpn-status">VPN Активен</div>
                <span id="statusText">Подключено через VLESS прокси • 127.0.0.1:1080</span>
            </div>
        </div>

        <script>
            const addressBar = document.getElementById('addressBar');
            const webview = document.getElementById('webview');
            const statusText = document.getElementById('statusText');
            
            // API для взаимодействия с Python
            const api = window.pywebview?.api || {{
                navigate: (url) => console.log('Navigate:', url),
                go_back: () => console.log('Go back'),
                go_forward: () => console.log('Go forward'),
                refresh: () => console.log('Refresh'),
                go_home: () => console.log('Go home')
            }};
            
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
                
                addressBar.value = url;
                statusText.textContent = 'Загрузка... • ' + url;
                
                if (api.navigate) {{
                    api.navigate(url);
                }} else {{
                    webview.src = url;
                }}
                
                setTimeout(() => {{
                    statusText.textContent = 'Загружено через VLESS прокси • 127.0.0.1:1080';
                }}, 1000);
            }}
            
            function goBack() {{
                if (api.go_back) {{
                    api.go_back();
                }} else {{
                    history.back();
                }}
            }}
            
            function goForward() {{
                if (api.go_forward) {{
                    api.go_forward();
                }} else {{
                    history.forward();
                }}
            }}
            
            function refresh() {{
                if (api.refresh) {{
                    api.refresh();
                }} else {{
                    location.reload();
                }}
            }}
            
            function goHome() {{
                navigate('{start_url}');
            }}
            
            function navigateToBookmark(url) {{
                if (url) {{
                    navigate(url);
                }}
                // Сбрасываем выбор
                event.target.selectedIndex = 0;
            }}
            
            // Обработка Enter в адресной строке
            addressBar.addEventListener('keypress', function(e) {{
                if (e.key === 'Enter') {{
                    navigate();
                }}
            }});
            
            // Автообновление адресной строки (если возможно)
            if (webview) {{
                webview.addEventListener('loadstart', function() {{
                    statusText.textContent = 'Загрузка...';
                }});
                
                webview.addEventListener('loadstop', function() {{
                    statusText.textContent = 'Загружено через VLESS прокси • 127.0.0.1:1080';
                    try {{
                        addressBar.value = webview.src;
                    }} catch(e) {{
                        // Игнорируем ошибки CORS
                    }}
                }});
            }}
        </script>
    </body>
    </html>
    """

    # Создаём API объект
    api = ModernBrowserApi()
    
    # Создаём окно безопасно
    window, supports_api_param = create_webview_window_safe(
        'Лёгкий браузер с VLESS VPN', 
        html, 
        api,
        width=1200,
        height=800,
        min_size=(800, 600)
    )

    # Запускаем webview безопасно
    start_webview_safe(api, supports_api_param)


if __name__ == '__main__':
    start()
