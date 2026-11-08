"""Декораторы и кэширование для базы данных."""

import time
from functools import wraps


def handle_db_errors(func):
    """Обрабатывает ошибки операций базы данных."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyError, ValueError, FileNotFoundError) as error:
            print(f"Ошибка базы данных: {error}")
            return None

    return wrapper


def confirm_action(action_name):
    """Запрашивает подтверждение опасной операции."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            answer = (
                input(f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ')
                .strip()
                .lower()
            )

            if answer != "y":
                print("Операция отменена.")
                return None

            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    """Измеряет время выполнения функции."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        elapsed = time.monotonic() - start

        print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд.")
        return result

    return wrapper


def create_cacher():
    """Создаёт кэш с возможностью очистки."""
    cache = {}

    def cache_result(key, value_func):
        if key not in cache:
            cache[key] = value_func()
        return cache[key]

    def clear_cache():
        cache.clear()

    return cache_result, clear_cache
