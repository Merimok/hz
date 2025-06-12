import json
import os
from urllib.parse import quote_plus
import webview


def start():
    """Запускает пользовательский интерфейс браузера с закладками."""
    bookmarks = []
    with open(os.path.join('resources', 'bookmarks.json'), 'r') as bf:
        bookmarks = json.load(bf)

    start_url = 'https://www.google.com'
    options = ''.join([f"<option value='{b['url']}'>{b['name']}</option>" for b in bookmarks])

    html = """
    <!DOCTYPE html>
    <html>
    <body style='margin:0;padding:0;'>
      <div style='display:flex; padding:5px; background:#eee;'>
        <button onclick=\"window.pywebview.api.goBack()\">\u2190</button>
        <button onclick=\"window.pywebview.api.goForward()\">\u2192</button>
        <button onclick=\"window.pywebview.api.refresh()\">\u27f3</button>
        <input id='address' style='flex:1;margin:0 5px;' value='{start}' />
        <button onclick=\"window.pywebview.api.navigate(document.getElementById('address').value)\">Go</button>
        <select onchange=\"window.pywebview.api.navigate(this.value)\">
          <option>\u0417\u0430\u043a\u043b\u0430\u0434\u043a\u0438</option>
          {options}
        </select>
      </div>
      <webview id='wv' src='{start}' style='width:100%; height:calc(100% - 40px);'></webview>
      <script>
        const api = window.pywebview.api;
        document.getElementById('address').addEventListener('keypress', e => { if (e.key === 'Enter') api.navigate(e.target.value); });
      </script>
    </body>
    </html>
    """.format(start=start_url, options=options)

    window = webview.create_window('Lightweight Browser', html)

    class Api:
        def navigate(self, text):
            url = text
            if not text.startswith('http://') and not text.startswith('https://'):
                url = 'https://www.google.com/search?q=' + quote_plus(text)
            window.load_url(url)
        def goBack(self):
            window.go_back()
        def goForward(self):
            window.go_forward()
        def refresh(self):
            window.reload()

    webview.start(gui='edgehtml' if os.name=='nt' else None, debug=True, http_server=True, js_api=Api())
