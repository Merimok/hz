#!/bin/bash

echo "🚀 Quick Push Script v3.0.0"
echo "=========================="

cd /home/tannim/hz

echo "📝 Добавляем изменения..."
git add -A

echo "💾 Создаем коммит..."
git commit -m "🔥 HOTFIX v3.0.0: Force push ultra-modern browser

- Ultra-Modern Material Design 3 UI
- Complete Tab Management System  
- Advanced Logging for debugging
- Cross-platform Windows + Linux support
- Ready for GitHub Actions build"

echo "📤 Пушим на GitHub..."
git push origin main

echo "🏷️ Создаем тег v3.0.0..."
git tag -f v3.0.0 -m "Ultra-Modern Browser v3.0.0"
git push origin v3.0.0 --force

echo "✅ Push завершен!"
echo "🔗 Проверьте GitHub Actions на: https://github.com/your-repo/actions"
