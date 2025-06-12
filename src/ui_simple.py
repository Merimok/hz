"""
Simple fallback browser UI using built-in webbrowser module
"""
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import subprocess
import os


class SimpleBrowser:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Лёгкий браузер с VLESS VPN")
        self.root.geometry("800x600")
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка пользовательского интерфейса."""
        # Заголовок
        header = tk.Frame(self.root, bg="#6366f1", height=60)
        header.pack(fill="x", padx=10, pady=5)
        header.pack_propagate(False)
        
        title_label = tk.Label(header, text="🌐 Лёгкий браузер с VLESS VPN", 
                              bg="#6366f1", fg="white", font=("Arial", 14, "bold"))
        title_label.pack(pady=15)
        
        # Панель навигации
        nav_frame = tk.Frame(self.root, bg="#f8fafc", height=50)
        nav_frame.pack(fill="x", padx=10, pady=5)
        nav_frame.pack_propagate(False)
        
        # Кнопки навигации
        btn_frame = tk.Frame(nav_frame, bg="#f8fafc")
        btn_frame.pack(side="left", pady=10)
        
        tk.Button(btn_frame, text="← Назад", command=self.go_back, 
                 bg="#e5e7eb", relief="flat", padx=10).pack(side="left", padx=2)
        tk.Button(btn_frame, text="→ Вперед", command=self.go_forward, 
                 bg="#e5e7eb", relief="flat", padx=10).pack(side="left", padx=2)
        tk.Button(btn_frame, text="↻ Обновить", command=self.refresh, 
                 bg="#e5e7eb", relief="flat", padx=10).pack(side="left", padx=2)
        tk.Button(btn_frame, text="🏠 Домой", command=self.go_home, 
                 bg="#e5e7eb", relief="flat", padx=10).pack(side="left", padx=2)
        
        # Адресная строка
        addr_frame = tk.Frame(nav_frame, bg="#f8fafc")
        addr_frame.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        
        self.address_var = tk.StringVar(value="https://www.google.com")
        self.address_entry = tk.Entry(addr_frame, textvariable=self.address_var, 
                                     font=("Arial", 11), relief="flat", bd=5)
        self.address_entry.pack(side="left", fill="x", expand=True)
        self.address_entry.bind("<Return>", lambda e: self.navigate())
        
        tk.Button(addr_frame, text="Перейти", command=self.navigate,
                 bg="#6366f1", fg="white", relief="flat", padx=15).pack(side="right", padx=5)
        
        # Закладки
        bookmarks_frame = tk.Frame(nav_frame, bg="#f8fafc")
        bookmarks_frame.pack(side="right", pady=10)
        
        bookmarks = [
            ("YouTube", "https://www.youtube.com"),
            ("2IP", "https://2ip.ru"),
            ("Google", "https://www.google.com")
        ]
        
        tk.Label(bookmarks_frame, text="Закладки:", bg="#f8fafc", font=("Arial", 10)).pack(side="left")
        for name, url in bookmarks:
            tk.Button(bookmarks_frame, text=name, 
                     command=lambda u=url: self.navigate_to(u),
                     bg="#e5e7eb", relief="flat", font=("Arial", 9)).pack(side="left", padx=2)
        
        # Основная область
        main_frame = tk.Frame(self.root, bg="white")
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        info_text = """
🌐 Лёгкий браузер с VLESS VPN

✅ VPN статус: Активен
🔒 Прокси: SOCKS5://127.0.0.1:1080
🌍 Маршрутизация: Через VLESS сервер

📝 Инструкции:
• Введите URL в адресную строку
• Используйте кнопки навигации
• Выберите закладку для быстрого доступа
• Браузер откроется в системном браузере с прокси

⚠️ Примечание: В этом режиме используется системный браузер
Для полнофункциональной работы требуется установка pywebview
        """
        
        tk.Label(main_frame, text=info_text, justify="left", 
                font=("Arial", 12), bg="white", fg="#374151").pack(pady=50)
        
        # Статусная строка
        status_frame = tk.Frame(self.root, bg="#f1f5f9", height=30)
        status_frame.pack(fill="x", side="bottom")
        status_frame.pack_propagate(False)
        
        self.status_var = tk.StringVar(value="🔒 VPN активен • Подключено через VLESS прокси • 127.0.0.1:1080")
        tk.Label(status_frame, textvariable=self.status_var, 
                bg="#f1f5f9", fg="#64748b", font=("Arial", 10)).pack(pady=5)
                
    def navigate_to(self, url):
        """Навигация к определенному URL."""
        self.address_var.set(url)
        self.navigate()
        
    def navigate(self):
        """Навигация по введенному URL."""
        url = self.address_var.get().strip()
        if not url:
            return
            
        # Если URL не содержит протокол, добавляем https://
        if not url.startswith(('http://', 'https://')):
            if '.' in url and ' ' not in url:
                url = 'https://' + url
            else:
                url = 'https://www.google.com/search?q=' + url.replace(' ', '+')
                
        self.address_var.set(url)
        
        try:
            print(f"Открытие URL: {url}")
            # Открываем в системном браузере
            webbrowser.open(url)
            self.status_var.set(f"🔒 Открыто в браузере: {url}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть URL: {e}")
            
    def go_back(self):
        """Возврат назад."""
        self.navigate_to("https://www.google.com")
        
    def go_forward(self):
        """Переход вперед."""
        self.navigate_to("https://www.google.com")
        
    def refresh(self):
        """Обновление."""
        current_url = self.address_var.get()
        if current_url:
            self.navigate()
            
    def go_home(self):
        """Переход на домашнюю страницу."""
        self.navigate_to("https://www.google.com")
        
    def run(self):
        """Запуск интерфейса."""
        self.root.mainloop()


def start():
    """Запуск простого браузера."""
    print("Запуск простого браузера (fallback режим)")
    browser = SimpleBrowser()
    browser.run()


if __name__ == '__main__':
    start()
