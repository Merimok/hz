import webview, json, os


def start():
    bookmarks = []
    with open(os.path.join('resources', 'bookmarks.json'), 'r') as bf:
        bookmarks = json.load(bf)

    html = f"""
    <!DOCTYPE html>
    <html>
    <body style='margin:0;padding:0;'>
      <div style='display:flex; padding:5px; background:#eee;'>
        <button onclick="window.pywebview.api.goBack()">\u2190</button>
        <button onclick="window.pywebview.api.goForward()">\u2192</button>
        <input id='url' style='flex:1;margin:0 5px;' value='https://example.com' />
        <button onclick="window.pywebview.api.navigate(document.getElementById('url').value)">Go</button>
        <select onchange="window.pywebview.api.navigate(this.value)">
          <option>\u0417\u0430\u043a\u043b\u0430\u0434\u043a\u0438</option>
          {''.join([f"<option value='{b['url']}'>{b['name']}</option>" for b in bookmarks])}
        </select>
      </div>
      <webview id='wv' src='https://example.com' style='width:100%; height:calc(100% - 40px);'></webview>
      <script>
        const api = window.pywebview.api;
        document.getElementById('url').onkeypress = e => {{ if (e.key === 'Enter') api.navigate(e.target.value); }};
      </script>
    </body>
    </html>
    """

    window = webview.create_window('Lightweight Browser', html)

    class Api:
        def navigate(self, url):
            window.load_url(url)
        def goBack(self):
            window.go_back()
        def goForward(self):
            window.go_forward()

    webview.start(gui='edgehtml' if os.name=='nt' else None, debug=True, http_server=True, js_api=Api())
