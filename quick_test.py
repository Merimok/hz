#!/usr/bin/env python3
"""
Простой тест браузера с вкладками (без GUI)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.core.tab_manager import TabManager
    print("✅ TabManager успешно импортирован")
    
    # Создаем менеджер вкладок
    tm = TabManager()
    print("✅ TabManager создан")
    
    # Создаем вкладку
    tab = tm.create_tab("https://www.google.com", "Google")
    print(f"✅ Создана вкладка: {tab.title}")
    
    # Проверяем количество вкладок
    print(f"📊 Всего вкладок: {len(tm.tabs)}")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()

print("🎉 Тест завершен")
