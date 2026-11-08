"""Основная логика управления таблицами."""

from primitive_db.constants import VALID_TYPES
from primitive_db.decorators import (
    confirm_action,
    handle_db_errors,
    log_time,
)


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Создаёт таблицу с заданными столбцами."""
    if table_name in metadata:
        raise ValueError(f'Таблица "{table_name}" уже существует.')

    if not columns:
        raise ValueError("Необходимо указать столбцы таблицы.")

    parsed_columns = {"ID": "int"}

    for column in columns:
        if ":" not in column:
            raise ValueError(f"Некорректное значение: {column}")

        name, data_type = column.split(":", 1)

        if not name or data_type not in VALID_TYPES:
            raise ValueError(f"Некорректное значение: {column}")

        if name in parsed_columns:
            raise ValueError(f"Столбец {name} уже существует.")

        parsed_columns[name] = data_type

    metadata[table_name] = parsed_columns
    return metadata


@confirm_action("удаление таблицы")
@handle_db_errors
def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных."""
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')

    del metadata[table_name]
    return metadata


def list_tables(metadata):
    """Возвращает список таблиц."""
    return list(metadata.keys())


def convert_value(value, data_type):
    """Преобразует значение в заданный тип."""
    if data_type == "int":
        return int(value)

    if data_type == "bool":
        if str(value).lower() == "true":
            return True
        if str(value).lower() == "false":
            return False
        raise ValueError(f"Некорректное значение bool: {value}")

    return str(value)


@log_time
@handle_db_errors
def insert(metadata, table_name, values):
    """Добавляет запись в таблицу."""
    from primitive_db.utils import load_table_data

    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')

    columns = metadata[table_name]
    field_names = list(columns.keys())[1:]

    if len(values) != len(field_names):
        raise ValueError("Неверное количество значений.")

    data = load_table_data(table_name)
    new_id = max((row["ID"] for row in data), default=0) + 1

    record = {"ID": new_id}

    for name, value in zip(field_names, values):
        record[name] = convert_value(value, columns[name])

    data.append(record)
    return data, new_id


@log_time
@handle_db_errors
def select(table_data, where_clause=None):
    """Возвращает записи по условию."""
    if where_clause is None:
        return table_data

    return [
        row
        for row in table_data
        if all(row.get(key) == value for key, value in where_clause.items())
    ]


@handle_db_errors
def update(table_data, set_clause, where_clause):
    """Обновляет записи по условию."""
    count = 0

    for row in table_data:
        if all(row.get(k) == v for k, v in where_clause.items()):
            row.update(set_clause)
            count += 1

    return table_data, count


@confirm_action("удаление записей")
@handle_db_errors
def delete(table_data, where_clause):
    """Удаляет записи по условию."""
    remaining = [
        row
        for row in table_data
        if not all(row.get(k) == v for k, v in where_clause.items())
    ]

    return remaining, len(table_data) - len(remaining)
