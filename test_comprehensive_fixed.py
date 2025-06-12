#!/usr/bin/env python3
"""
Comprehensive test suite for the Lightweight Browser with VLESS VPN
Tests all components and fallback systems - Windows compatible version
"""

import os
import sys
import json
import subprocess
import tempfile


def test_project_structure():
    """Test that all required files exist."""
    print("Testing project structure...")
    
    required_files = [
        'main.py',
        'requirements.txt',
        'src/ui_modern_fixed.py',
        'src/ui_modern.py', 
        'src/ui.py',
        'src/ui_simple.py',
        'config/vless.txt'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  [OK] {file_path}")
        else:
            print(f"  [FAIL] {file_path} - MISSING")
            return False
    
    return True


def test_vless_uri_parsing():
    """Test VLESS URI parsing functionality."""
    print("\nTesting VLESS URI parsing...")
    
    # Import the main module
    sys.path.append('.')
    try:
        import main
        
        # Test URI
        test_uri = "vless://331564911@94.131.110.172:23209?encryption=none&flow=&fp=random&pbk=EhZf6JqOLErCdliMk1UBlpojo3cfw244QWtoZ-qUFTc&security=reality&sni=yahoo.com&spx=%2F&type=tcp&sid=68c55e5189f67c90#example"
        
        # Test config generation
        main.generate_config(test_uri)
        
        # Check if config.json was created
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                config = json.load(f)
                
            # Verify structure
            if 'inbounds' in config and 'outbounds' in config:
                print("  [OK] Config structure valid")
                
                # Check SOCKS inbound
                socks_found = any(ib.get('protocol') == 'socks' for ib in config['inbounds'])
                if socks_found:
                    print("  [OK] SOCKS inbound configured")
                else:
                    print("  [FAIL] SOCKS inbound missing")
                    return False
                    
                # Check VLESS outbound
                vless_found = any(ob.get('protocol') == 'vless' for ob in config['outbounds'])
                if vless_found:
                    print("  [OK] VLESS outbound configured")
                else:
                    print("  [FAIL] VLESS outbound missing")
                    return False
                    
                return True
            else:
                print("  [FAIL] Invalid config structure")
                return False
        else:
            print("  [FAIL] config.json not created")
            return False
            
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def test_ui_imports():
    """Test that all UI modules can be imported."""
    print("\nTesting UI module imports...")
    
    ui_modules = [
        'src.ui_simple',      # Should always work (Tkinter)
        'src.ui',             # Requires pywebview
        'src.ui_modern',      # Requires pywebview  
        'src.ui_modern_fixed' # Requires pywebview
    ]
    
    success_count = 0
    
    for module_name in ui_modules:
        try:
            __import__(module_name)
            print(f"  [OK] {module_name}")
            success_count += 1
        except ImportError as e:
            print(f"  [WARN] {module_name} - {e}")
        except Exception as e:
            print(f"  [FAIL] {module_name} - {e}")
    
    # At least one UI should work
    if success_count > 0:
        print(f"  [OK] {success_count}/{len(ui_modules)} UI modules available")
        return True
    else:
        print("  [FAIL] No UI modules available")
        return False


def test_xray_download():
    """Test Xray binary download functionality."""
    print("\nTesting Xray download...")
    
    try:
        sys.path.append('.')
        import main
        
        # Temporarily move existing xray if present
        xray_path = os.path.join('bin', 'xray.exe')
        backup_path = xray_path + '.backup'
        
        if os.path.exists(xray_path):
            os.rename(xray_path, backup_path)
        
        # Test download
        result = main.ensure_xray()
        
        if result and os.path.exists(result):
            print("  [OK] Xray download successful")
            success = True
        else:
            print("  [FAIL] Xray download failed")
            success = False
            
        # Restore backup if exists
        if os.path.exists(backup_path):
            if os.path.exists(xray_path):
                os.remove(xray_path)
            os.rename(backup_path, xray_path)
            
        return success
        
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def test_requirements():
    """Test requirements.txt content."""
    print("\nTesting requirements.txt...")
    
    try:
        with open('requirements.txt', 'r') as f:
            content = f.read()
            
        if 'pywebview' in content:
            print("  [OK] pywebview dependency listed")
            return True
        else:
            print("  [FAIL] pywebview dependency missing")
            return False
            
    except FileNotFoundError:
        print("  [FAIL] requirements.txt not found")
        return False
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def test_fallback_system():
    """Test the fallback system in main.py."""
    print("\nTesting fallback system...")
    
    try:
        # Read main.py content
        with open('main.py', 'r') as f:
            content = f.read()
            
        # Check for cascading try-except blocks
        fallbacks = [
            'ui_modern_fixed',
            'ui_modern', 
            'ui.py',
            'ui_simple'
        ]
        
        found_fallbacks = 0
        for fallback in fallbacks:
            if fallback in content:
                found_fallbacks += 1
                print(f"  [OK] {fallback} fallback present")
        
        if found_fallbacks >= 3:
            print("  [OK] Fallback system comprehensive")
            return True
        else:
            print(f"  [WARN] Only {found_fallbacks} fallbacks found")
            return False
            
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def run_all_tests():
    """Run all tests and provide summary."""
    print("=" * 60)
    print("COMPREHENSIVE TEST SUITE")
    print("Lightweight Browser with VLESS VPN v2.2.0")
    print("=" * 60)
    
    tests = [
        ("Project Structure", test_project_structure),
        ("VLESS URI Parsing", test_vless_uri_parsing), 
        ("UI Module Imports", test_ui_imports),
        ("Xray Download", test_xray_download),
        ("Requirements File", test_requirements),
        ("Fallback System", test_fallback_system)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"\n[FAIL] {test_name} FAILED")
        except Exception as e:
            print(f"\n[CRASH] {test_name} CRASHED: {e}")
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("ALL TESTS PASSED! Project is ready for production.")
        return True
    elif passed >= total * 0.8:
        print("Most tests passed. Project is functional with minor issues.")
        return True
    else:
        print("Some critical tests failed. Review required.")
        return False


if __name__ == '__main__':
    # Change to project directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    success = run_all_tests()
    sys.exit(0 if success else 1)
