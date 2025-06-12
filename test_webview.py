#!/usr/bin/env python3
"""
Test script to verify pywebview installation and basic functionality
"""

try:
    import webview
    print(f"✅ PyWebview imported successfully. Version: {webview.__version__}")
    
    # Test simple window creation (but don't start it)
    print("✅ Testing window creation...")
    window = webview.create_window('Test', '<h1>Test</h1>', width=400, height=300)
    print("✅ Window creation successful")
    
    print("\n🎉 All tests passed! The application should work.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install pywebview: pip3 install pywebview>=4.0.0")
    
except Exception as e:
    print(f"❌ Error: {e}")
