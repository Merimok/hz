#!/usr/bin/env python3
"""
Тестирование системы вкладок TabManager
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.tab_manager import TabManager

def test_tab_manager():
    """Тестирование функций TabManager"""
    print("🗂️ ТЕСТИРОВАНИЕ СИСТЕМЫ ВКЛАДОК")
    print("=" * 50)
    
    # Создаем менеджер вкладок
    tab_manager = TabManager()
    
    # Создаем первую вкладку
    tab1 = tab_manager.create_tab("https://www.google.com", "Google")
    print(f"✅ Создана вкладка 1: {tab1.title} ({tab1.url})")
    
    # Создаем вторую вкладку
    tab2 = tab_manager.create_tab("https://www.youtube.com", "YouTube")
    print(f"✅ Создана вкладка 2: {tab2.title} ({tab2.url})")
    
    # Создаем третью вкладку
    tab3 = tab_manager.create_tab("https://github.com", "GitHub")
    print(f"✅ Создана вкладка 3: {tab3.title} ({tab3.url})")
    
    print(f"\n📊 Всего вкладок: {len(tab_manager.tabs)}")
    print(f"🎯 Активная вкладка: {tab_manager.get_active_tab().title}")
    
    # Закрепляем первую вкладку
    tab_manager.pin_tab(tab1.id)
    print(f"📌 Закреплена вкладка: {tab1.title}")
    
    # Переключаемся на вторую вкладку
    tab_manager.switch_tab(tab2.id)
    print(f"🔄 Переключились на: {tab_manager.get_active_tab().title}")
    
    # Дублируем активную вкладку
    duplicated = tab_manager.duplicate_tab(tab2.id)
    if duplicated:
        print(f"📄 Дублирована вкладка: {duplicated.title}")
    
    # Показываем все вкладки
    print("\n📋 СПИСОК ВСЕХ ВКЛАДОК:")
    for i, tab in enumerate(tab_manager.tabs, 1):
        status = "🎯 АКТИВНАЯ" if tab.id == tab_manager.active_tab_id else ""
        pinned = "📌 ЗАКРЕПЛЕНА" if tab.is_pinned else ""
        print(f"  {i}. {tab.title} - {tab.url} {status} {pinned}")
    
    # Закрываем одну вкладку
    print(f"\n❌ Закрываем вкладку: {tab3.title}")
    tab_manager.close_tab(tab3.id)
    print(f"📊 Осталось вкладок: {len(tab_manager.tabs)}")
    
    # Сохраняем сессию
    print("\n💾 Сохраняем сессию...")
    tab_manager.save_session()
    
    # Показываем статистику
    print("\n📈 СТАТИСТИКА:")
    stats = tab_manager.get_session_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")

if __name__ == "__main__":
    test_tab_manager()
