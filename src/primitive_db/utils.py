"""Функции для работы с JSON-файлами."""

import json
from pathlib import Path

DATA_DIR = Path("data")


def load_metadata(filepath):
    """Загружает метаданные из JSON-файла."""
    try:
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    """Сохраняет метаданные в JSON-файл."""
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_table_data(table_name):
    """Загружает записи таблицы из JSON."""
    filepath = DATA_DIR / f"{table_name}.json"

    try:
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_table_data(table_name, data):
    """Сохраняет записи таблицы в JSON."""
    DATA_DIR.mkdir(exist_ok=True)
    filepath = DATA_DIR / f"{table_name}.json"

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def delete_table_data(table_name):
    """Удаляет JSON-файл таблицы."""
    filepath = DATA_DIR / f"{table_name}.json"

    if filepath.exists():
        filepath.unlink()
