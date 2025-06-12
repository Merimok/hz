#!/usr/bin/env python3
"""
Tab Manager System - Core component for modern browser
Система управления вкладками для современного браузера
"""

import uuid
import json
import threading
from datetime import datetime
from typing import List, Optional, Dict
import webview


class Tab:
    """Представляет одну вкладку браузера."""
    
    def __init__(self, url: str = "about:blank", title: str = "Новая вкладка"):
        self.id = str(uuid.uuid4())
        self.url = url
        self.title = title
        self.favicon = None
        self.is_loading = False
        self.is_pinned = False
        self.is_muted = False
        self.webview_instance = None
        self.created_at = datetime.now()
        self.last_visited = datetime.now()
        self.visit_count = 0
        
    def to_dict(self) -> Dict:
        """Сериализация вкладки в словарь."""
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'is_pinned': self.is_pinned,
            'is_muted': self.is_muted,
            'created_at': self.created_at.isoformat(),
            'last_visited': self.last_visited.isoformat(),
            'visit_count': self.visit_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Tab':
        """Десериализация вкладки из словаря."""
        tab = cls(data['url'], data['title'])
        tab.id = data['id']
        tab.is_pinned = data.get('is_pinned', False)
        tab.is_muted = data.get('is_muted', False)
        tab.visit_count = data.get('visit_count', 0)
        return tab


class TabManager:
    """Менеджер вкладок браузера."""
    
    def __init__(self, max_tabs: int = 20):
        self.tabs: List[Tab] = []
        self.active_tab_id: Optional[str] = None
        self.max_tabs = max_tabs
        self.session_file = "data/tabs_session.json"
        self._tab_callbacks = []
        
        # Создаем папку для данных
        import os
        os.makedirs("data", exist_ok=True)
        
    def add_callback(self, callback):
        """Добавляет callback для уведомлений об изменениях вкладок."""
        self._tab_callbacks.append(callback)
        
    def _notify_callbacks(self, event_type: str, tab_id: str = None):
        """Уведомляет все callbacks об изменениях."""
        for callback in self._tab_callbacks:
            try:
                callback(event_type, tab_id)
            except Exception as e:
                print(f"Ошибка в callback: {e}")
    
    def create_tab(self, url: str = "https://www.google.com", title: str = None, activate: bool = True) -> Tab:
        """Создает новую вкладку."""
        if len(self.tabs) >= self.max_tabs:
            raise Exception(f"Достигнуто максимальное количество вкладок ({self.max_tabs})")
        
        if title is None:
            title = "Загрузка..." if url != "about:blank" else "Новая вкладка"
            
        tab = Tab(url, title)
        
        # Добавляем в конец, но после закрепленных вкладок
        pinned_count = sum(1 for t in self.tabs if t.is_pinned)
        self.tabs.insert(pinned_count, tab)
        
        if activate or not self.active_tab_id:
            self.switch_to_tab(tab.id)
            
        self._notify_callbacks("tab_created", tab.id)
        self.save_session()
        return tab
    
    def close_tab(self, tab_id: str) -> bool:
        """Закрывает вкладку по ID."""
        tab = self.get_tab(tab_id)
        if not tab:
            return False
            
        # Нельзя закрыть последнюю вкладку
        if len(self.tabs) == 1:
            # Вместо закрытия создаем новую пустую вкладку
            self.create_tab("about:blank", "Новая вкладка")
            
        tab_index = self.tabs.index(tab)
        self.tabs.remove(tab)
        
        # Если закрыли активную вкладку, переключаемся на соседнюю
        if self.active_tab_id == tab_id:
            if tab_index < len(self.tabs):
                next_tab = self.tabs[tab_index]
            elif tab_index > 0:
                next_tab = self.tabs[tab_index - 1]
            else:
                next_tab = self.tabs[0] if self.tabs else None
                
            if next_tab:
                self.switch_to_tab(next_tab.id)
            else:
                self.active_tab_id = None
        
        # Очистка webview instance
        if tab.webview_instance:
            try:
                tab.webview_instance.destroy()
            except:
                pass
                
        self._notify_callbacks("tab_closed", tab_id)
        self.save_session()
        return True
    
    def switch_to_tab(self, tab_id: str) -> bool:
        """Переключается на указанную вкладку."""
        tab = self.get_tab(tab_id)
        if not tab:
            return False
            
        old_active_id = self.active_tab_id
        self.active_tab_id = tab_id
        tab.last_visited = datetime.now()
        tab.visit_count += 1
        
        self._notify_callbacks("tab_activated", tab_id)
        if old_active_id and old_active_id != tab_id:
            self._notify_callbacks("tab_deactivated", old_active_id)
            
        self.save_session()
        return True
    
    def move_tab(self, tab_id: str, new_index: int) -> bool:
        """Перемещает вкладку на новую позицию."""
        tab = self.get_tab(tab_id)
        if not tab:
            return False
            
        old_index = self.tabs.index(tab)
        if old_index == new_index:
            return True
            
        # Нельзя перемещать обычные вкладки перед закрепленными
        pinned_count = sum(1 for t in self.tabs if t.is_pinned)
        if not tab.is_pinned and new_index < pinned_count:
            new_index = pinned_count
            
        self.tabs.pop(old_index)
        self.tabs.insert(new_index, tab)
        
        self._notify_callbacks("tab_moved", tab_id)
        self.save_session()
        return True
    
    def pin_tab(self, tab_id: str) -> bool:
        """Закрепляет вкладку."""
        tab = self.get_tab(tab_id)
        if not tab:
            return False
            
        tab.is_pinned = True
        
        # Перемещаем в начало к другим закрепленным
        self.tabs.remove(tab)
        pinned_count = sum(1 for t in self.tabs if t.is_pinned)
        self.tabs.insert(pinned_count, tab)
        
        self._notify_callbacks("tab_pinned", tab_id)
        self.save_session()
        return True
    
    def unpin_tab(self, tab_id: str) -> bool:
        """Открепляет вкладку."""
        tab = self.get_tab(tab_id)
        if not tab:
            return False
            
        tab.is_pinned = False
        self._notify_callbacks("tab_unpinned", tab_id)
        self.save_session()
        return True
    
    def duplicate_tab(self, tab_id: str) -> Optional[Tab]:
        """Дублирует вкладку."""
        tab = self.get_tab(tab_id)
        if not tab:
            return None
            
        new_tab = self.create_tab(tab.url, tab.title, activate=True)
        return new_tab
    
    def get_tab(self, tab_id: str) -> Optional[Tab]:
        """Получает вкладку по ID."""
        for tab in self.tabs:
            if tab.id == tab_id:
                return tab
        return None
    
    def get_active_tab(self) -> Optional[Tab]:
        """Получает активную вкладку."""
        if self.active_tab_id:
            return self.get_tab(self.active_tab_id)
        return None
    
    def get_tab_index(self, tab_id: str) -> int:
        """Получает индекс вкладки."""
        tab = self.get_tab(tab_id)
        if tab:
            return self.tabs.index(tab)
        return -1
    
    def close_other_tabs(self, keep_tab_id: str) -> int:
        """Закрывает все вкладки кроме указанной."""
        tabs_to_close = [tab.id for tab in self.tabs if tab.id != keep_tab_id and not tab.is_pinned]
        closed_count = 0
        
        for tab_id in tabs_to_close:
            if self.close_tab(tab_id):
                closed_count += 1
                
        return closed_count
    
    def close_tabs_to_right(self, tab_id: str) -> int:
        """Закрывает все вкладки справа от указанной."""
        tab_index = self.get_tab_index(tab_id)
        if tab_index == -1:
            return 0
            
        tabs_to_close = [tab.id for tab in self.tabs[tab_index + 1:] if not tab.is_pinned]
        closed_count = 0
        
        for close_tab_id in tabs_to_close:
            if self.close_tab(close_tab_id):
                closed_count += 1
                
        return closed_count
    
    def restore_last_closed_tab(self) -> Optional[Tab]:
        """Восстанавливает последнюю закрытую вкладку (заглушка)."""
        # TODO: Реализовать историю закрытых вкладок
        return self.create_tab("about:blank", "Восстановленная вкладка")
    
    def save_session(self):
        """Сохраняет текущую сессию вкладок."""
        session_data = {
            'tabs': [tab.to_dict() for tab in self.tabs],
            'active_tab_id': self.active_tab_id,
            'saved_at': datetime.now().isoformat()
        }
        
        try:
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения сессии: {e}")
    
    def load_session(self) -> bool:
        """Загружает сохраненную сессию вкладок."""
        try:
            with open(self.session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
                
            self.tabs = []
            for tab_data in session_data.get('tabs', []):
                tab = Tab.from_dict(tab_data)
                self.tabs.append(tab)
                
            self.active_tab_id = session_data.get('active_tab_id')
            
            # Если нет вкладок, создаем одну по умолчанию
            if not self.tabs:
                self.create_tab()
                
            return True
            
        except FileNotFoundError:
            # Первый запуск - создаем вкладку по умолчанию
            self.create_tab()
            return True
        except Exception as e:
            print(f"Ошибка загрузки сессии: {e}")
            # В случае ошибки создаем вкладку по умолчанию
            self.create_tab()
            return False
    
    def get_stats(self) -> Dict:
        """Получает статистику по вкладкам."""
        return {
            'total_tabs': len(self.tabs),
            'pinned_tabs': sum(1 for t in self.tabs if t.is_pinned),
            'active_tab_id': self.active_tab_id,
            'session_file_exists': os.path.exists(self.session_file)
        }


# Демонстрационный пример использования
if __name__ == "__main__":
    import os
    
    # Создаем менеджер вкладок
    tab_manager = TabManager()
    
    # Callback для отслеживания изменений
    def on_tab_change(event_type, tab_id):
        print(f"Событие: {event_type}, вкладка: {tab_id}")
    
    tab_manager.add_callback(on_tab_change)
    
    # Загружаем сохраненную сессию
    tab_manager.load_session()
    
    # Демонстрация функций
    print("=== ДЕМОНСТРАЦИЯ МЕНЕДЖЕРА ВКЛАДОК ===")
    
    # Создаем несколько вкладок
    tab1 = tab_manager.create_tab("https://www.google.com", "Google")
    tab2 = tab_manager.create_tab("https://www.youtube.com", "YouTube")
    tab3 = tab_manager.create_tab("https://github.com", "GitHub")
    
    print(f"Создано вкладок: {len(tab_manager.tabs)}")
    print(f"Активная вкладка: {tab_manager.get_active_tab().title}")
    
    # Закрепляем первую вкладку
    tab_manager.pin_tab(tab1.id)
    print(f"Закреплена вкладка: {tab1.title}")
    
    # Переключаемся между вкладками
    tab_manager.switch_to_tab(tab2.id)
    print(f"Переключились на: {tab_manager.get_active_tab().title}")
    
    # Дублируем вкладку
    duplicated = tab_manager.duplicate_tab(tab2.id)
    print(f"Дублирована вкладка: {duplicated.title}")
    
    # Закрываем вкладку
    tab_manager.close_tab(tab3.id)
    print(f"Осталось вкладок: {len(tab_manager.tabs)}")
    
    # Статистика
    stats = tab_manager.get_stats()
    print(f"Статистика: {stats}")
    
    # Сохраняем сессию
    tab_manager.save_session()
    print("Сессия сохранена")
