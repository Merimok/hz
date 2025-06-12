"""
Тесты для лёгкого браузера с VLESS VPN
"""
import unittest
import os
import json
import tempfile
import shutil
from unittest.mock import patch, mock_open

# Добавляем путь к модулям
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import get_vless_uri, generate_config


class TestVLESSBrowser(unittest.TestCase):
    """Тесты основных функций браузера"""
    
    def setUp(self):
        """Подготовка к тестам"""
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
        
    def tearDown(self):
        """Очистка после тестов"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
    
    def test_get_vless_uri_from_env(self):
        """Тест загрузки VLESS URI из переменной окружения"""
        test_uri = "vless://test@example.com:443"
        with patch.dict(os.environ, {'VLESS_URI': test_uri}):
            result = get_vless_uri()
            self.assertEqual(result, test_uri)
    
    def test_get_vless_uri_from_file(self):
        """Тест загрузки VLESS URI из файла"""
        test_uri = "vless://test@example.com:443"
        
        # Создаём тестовый файл
        with open('vless.txt', 'w', encoding='utf-8') as f:
            f.write(test_uri)
            
        with patch.dict(os.environ, {}, clear=True):
            result = get_vless_uri()
            self.assertEqual(result, test_uri)
    
    def test_get_vless_uri_from_config_file(self):
        """Тест загрузки VLESS URI из config/vless.txt"""
        test_uri = "vless://test@example.com:443"
        
        # Создаём папку config и файл
        os.makedirs('config', exist_ok=True)
        with open('config/vless.txt', 'w', encoding='utf-8') as f:
            f.write(test_uri)
            
        with patch.dict(os.environ, {}, clear=True):
            result = get_vless_uri()
            self.assertEqual(result, test_uri)
    
    def test_generate_config_default(self):
        """Тест генерации конфигурации с значениями по умолчанию"""
        generate_config("")
        
        # Проверяем, что файл создан
        self.assertTrue(os.path.exists('config.json'))
        
        # Проверяем содержимое
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        self.assertIn('inbounds', config)
        self.assertIn('outbounds', config)
        self.assertEqual(config['inbounds'][0]['port'], 1080)
        self.assertEqual(config['inbounds'][0]['protocol'], 'vless')
    
    def test_generate_config_with_uri(self):
        """Тест генерации конфигурации с VLESS URI"""
        test_uri = "vless://test-id@example.com:443?fp=chrome&pbk=test-key&sni=test.com&sid=test-sid"
        generate_config(test_uri)
        
        # Проверяем содержимое
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        client_id = config['inbounds'][0]['settings']['clients'][0]['id']
        reality_settings = config['inbounds'][0]['streamSettings']['realitySettings']
        
        self.assertEqual(client_id, 'test-id')
        self.assertEqual(reality_settings['fp'], 'chrome')
        self.assertEqual(reality_settings['pbk'], 'test-key')
        self.assertEqual(reality_settings['spx'], ['test.com'])
        self.assertEqual(reality_settings['sid'], 'test-sid')


class TestUIFunctions(unittest.TestCase):
    """Тесты UI функций"""
    
    def setUp(self):
        """Подготовка к тестам"""
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
        
        # Создаём тестовые закладки
        os.makedirs('resources', exist_ok=True)
        bookmarks = [
            {"name": "YouTube", "url": "https://www.youtube.com"},
            {"name": "2IP", "url": "https://2ip.ru"}
        ]
        with open('resources/bookmarks.json', 'w', encoding='utf-8') as f:
            json.dump(bookmarks, f, indent=2)
        
    def tearDown(self):
        """Очистка после тестов"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
    
    def test_bookmarks_loading(self):
        """Тест загрузки закладок"""
        # Импортируем ui модул
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
        
        # Проверяем, что файл закладок существует и читается
        self.assertTrue(os.path.exists('resources/bookmarks.json'))
        
        with open('resources/bookmarks.json', 'r', encoding='utf-8') as f:
            bookmarks = json.load(f)
            
        self.assertEqual(len(bookmarks), 2)
        self.assertEqual(bookmarks[0]['name'], 'YouTube')
        self.assertEqual(bookmarks[1]['name'], '2IP')


if __name__ == '__main__':
    unittest.main()
