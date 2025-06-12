#!/usr/bin/env python3
"""
Logger System for Browser
Система логирования для браузера
"""

import os
import logging
import datetime
from pathlib import Path


def setup_logger(name="browser", log_level=logging.DEBUG):
    """Настройка логгера с записью в файл и консоль."""
    
    # Создаем папку для логов
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Имя файла с датой
    log_filename = f"browser_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_filepath = log_dir / log_filename
    
    # Настройка логгера
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Удаляем существующие обработчики, если есть
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Формат логов
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Обработчик для файла
    file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Обработчик для консоли
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(levelname)-8s | %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    logger.info(f"Логирование настроено. Файл логов: {log_filepath}")
    logger.info("=" * 60)
    
    return logger


def log_exception(logger, e, context=""):
    """Логирование исключений с контекстом."""
    logger.error(f"ОШИБКА{' в ' + context if context else ''}: {type(e).__name__}: {str(e)}")
    import traceback
    logger.debug(f"Полный traceback:\n{traceback.format_exc()}")


# Глобальный логгер для браузера
browser_logger = setup_logger("browser")
