#!/bin/bash
# GitHub Actions Plugin Fix Script
# This script ensures the correct generated_plugins.cmake is used

echo "🔧 Applying GitHub Actions plugin fix..."

# Backup original if it exists
if [ -f "windows/flutter/generated_plugins.cmake" ]; then
    cp "windows/flutter/generated_plugins.cmake" "windows/flutter/generated_plugins_original_backup.cmake"
    echo "✅ Backed up original generated_plugins.cmake"
fi

# Copy our GitHub Actions compatible version
cp "windows/flutter/generated_plugins_fixed.cmake" "windows/flutter/generated_plugins.cmake"
echo "✅ Applied GitHub Actions compatible generated_plugins.cmake"

# Make the file read-only to prevent Flutter from overwriting it
chmod 444 "windows/flutter/generated_plugins.cmake"
echo "✅ Protected file from overwriting"

echo "🚀 GitHub Actions plugin fix applied successfully!"
