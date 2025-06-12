import os
import subprocess
import threading
import webview
import json
import urllib.request
import zipfile
import io
from urllib.parse import urlparse, parse_qs


def get_vless_uri():
    """Load VLESS URI from environment variable or vless.txt file."""
    uri = os.getenv('VLESS_URI')
    if not uri:
        try:
            with open('vless.txt', 'r', encoding='utf-8') as f:
                uri = f.readline().strip()
        except FileNotFoundError:
            try:
                with open(os.path.join('config', 'vless.txt'), 'r', encoding='utf-8') as f:
                    uri = f.readline().strip()
            except FileNotFoundError:
                print("VLESS URI not found. Check vless.txt file or VLESS_URI environment variable")
                uri = ''
    return uri


def generate_config(uri: str):
    """Generate config.json configuration based on VLESS URI."""
    # Default values
    cfg = {
        'id': '331564911',
        'address': '94.131.110.172',
        'port': 23209,
        'fp': 'random',
        'pbk': 'EhZf6JqOLErCdliMk1UBlpojo3cfw244QWtoZ-qUFTc',
        'sni': 'yahoo.com',
        'sid': '68c55e5189f67c90'
    }
    
    # Parse VLESS URI
    if uri and uri.startswith('vless://'):
        try:
            parsed = urlparse(uri)
            print(f"Parsing URI: {uri}")
            
            # Extract ID (username)
            if parsed.username:
                cfg['id'] = parsed.username
                print(f"ID: {cfg['id']}")
            
            # Extract address and port
            if parsed.hostname:
                cfg['address'] = parsed.hostname
                print(f"Address: {cfg['address']}")
            
            if parsed.port:
                cfg['port'] = parsed.port
                print(f"Port: {cfg['port']}")
            
            # Parse query parameters
            qs = parse_qs(parsed.query)
            if 'fp' in qs:
                cfg['fp'] = qs['fp'][0]
                print(f"Fingerprint: {cfg['fp']}")
            if 'pbk' in qs:
                cfg['pbk'] = qs['pbk'][0]
                print(f"Public Key: {cfg['pbk'][:20]}...")
            if 'sni' in qs:
                cfg['sni'] = qs['sni'][0]
                print(f"SNI: {cfg['sni']}")
            if 'sid' in qs:
                cfg['sid'] = qs['sid'][0]
                print(f"Short ID: {cfg['sid']}")
                
        except Exception as e:
            print(f"Error parsing VLESS URI: {e}")
            print("Using default values")
    else:
        print("VLESS URI not found, using default values")

    # Generate proper configuration for Xray-core
    config = {
        'log': {
            'loglevel': 'info'
        },
        'inbounds': [
            {
                'port': 1080,
                'listen': '127.0.0.1',
                'protocol': 'socks',
                'sniffing': {
                    'enabled': True,
                    'destOverride': ['http', 'tls']
                },
                'settings': {
                    'auth': 'noauth',
                    'udp': True
                }
            }
        ],
        'outbounds': [
            {
                'protocol': 'vless',
                'settings': {
                    'vnext': [
                        {
                            'address': cfg['address'],
                            'port': cfg['port'],
                            'users': [
                                {
                                    'id': cfg['id'],
                                    'encryption': 'none'
                                }
                            ]
                        }
                    ]
                },
                'streamSettings': {
                    'network': 'tcp',
                    'security': 'reality',
                    'realitySettings': {
                        'show': False,
                        'fingerprint': cfg['fp'],
                        'serverName': cfg['sni'],
                        'publicKey': cfg['pbk'],
                        'shortId': cfg['sid']
                    }
                }
            }
        ]
    }
    
    print(f"Creating configuration for server {cfg['address']}:{cfg['port']}")
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print("Configuration config.json successfully created")


def ensure_xray():
    """Check for xray.exe presence and download if necessary."""
    xray_path = os.path.join('bin', 'xray.exe')
    
    # Create bin folder if it doesn't exist
    os.makedirs('bin', exist_ok=True)
    
    if os.path.exists(xray_path):
        print(f"Xray found: {xray_path}")
        return xray_path
    
    print("Xray not found. Downloading from GitHub...")
    url = 'https://github.com/XTLS/Xray-core/releases/latest/download/Xray-windows-64.zip'
    
    try:
        print('Downloading Xray-core...')
        data = urllib.request.urlopen(url).read()
        
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            for name in zf.namelist():
                if name.endswith('xray.exe'):
                    with open(xray_path, 'wb') as f:
                        f.write(zf.read(name))
                    print(f"Xray successfully downloaded: {xray_path}")
                    return xray_path
                    
        print("xray.exe not found in archive")
        return None
        
    except Exception as e:
        print(f"Error downloading Xray: {e}")
        return None


def start_xray():
    """Start Xray-core with binary download if necessary."""
    xray_path = ensure_xray()
    if not xray_path:
        print("Failed to obtain Xray-core. Continuing without VPN.")
        return
    
    try:
        print(f"Starting Xray: {xray_path}")
        process = subprocess.Popen([xray_path, 'run', '-c', 'config.json'])
        print(f"Xray started with PID: {process.pid}")
    except FileNotFoundError:
        print('Xray executable file not found.')
    except Exception as e:
        print(f'Error starting Xray: {e}')


def main():
    """Main application function."""
    print("=== Lightweight Browser with VLESS VPN ===")
    
    # Load and check VLESS URI
    uri = get_vless_uri()
    if not uri:
        print("Warning: VLESS URI not configured")
    
    # Generate configuration
    generate_config(uri)
    
    # Start Xray in background
    xray_thread = threading.Thread(target=start_xray)
    xray_thread.daemon = True
    xray_thread.start()
    
    # UI cascade fallback system
    ui_modules = [
        ('src.ui_modern_fixed', 'Modern UI with fixed pywebview 4.0+ compatibility'),
        ('src.ui_modern', 'Alternative modern UI'),
        ('src.ui', 'Basic UI with pywebview'),
        ('src.ui_simple', 'Fallback UI with Tkinter (no pywebview required)')
    ]
    
    for module_name, description in ui_modules:
        try:
            print(f"Attempting to load: {description}")
            ui_module = __import__(module_name, fromlist=[''])
            
            if hasattr(ui_module, 'create_browser'):
                print(f"Successfully loaded {module_name}")
                ui_module.create_browser()
                break
            else:
                print(f"Module {module_name} does not have create_browser function")
                
        except ImportError as e:
            print(f"Failed to import {module_name}: {e}")
            continue
        except Exception as e:
            print(f"Error starting {module_name}: {e}")
            continue
    else:
        print("ERROR: All UI modules failed to load!")
        print("Please check:")
        print("1. pywebview installation: pip install pywebview")
        print("2. tkinter availability (usually included with Python)")
        print("3. System dependencies for GUI applications")
        

if __name__ == '__main__':
    main()
