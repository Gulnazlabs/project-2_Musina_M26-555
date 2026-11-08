"""Консольный интерфейс базы данных."""

import re
import shlex

from prettytable import PrettyTable

from primitive_db.constants import META_FILE
from primitive_db.core import (
    convert_value,
    create_table,
    delete,
    drop_table,
    insert,
    list_tables,
    select,
    update,
)
from primitive_db.decorators import create_cacher
from primitive_db.parser import parse_condition, parse_values
from primitive_db.utils import (
    delete_table_data,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

cache_result, clear_cache = create_cacher()


def print_help():
    """Показывает доступные команды."""
    print("\n*** Примитивная база данных ***")
    print("create_table <имя> <столбец:тип> ...")
    print("list_tables")
    print("drop_table <имя>")
    print("insert into <имя> values (...)")
    print("select from <имя> [where <поле> = <значение>]")
    print("update <имя> set <поле> = <значение> where ...")
    print("delete from <имя> where <поле> = <значение>")
    print("info <имя>")
    print("help")
    print("exit\n")


def check_table(metadata, table_name):
    """Проверяет существование таблицы."""
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')


def typed_condition(text, columns):
    """Проверяет поле и преобразует значение условия."""
    condition = parse_condition(text)
    field, value = next(iter(condition.items()))

    if field not in columns:
        raise ValueError(f"Столбец {field} не существует.")

    return {field: convert_value(value, columns[field])}


def print_records(records, columns):
    """Выводит записи с помощью PrettyTable."""
    table = PrettyTable()
    table.field_names = list(columns)

    for record in records:
        table.add_row([record.get(name) for name in columns])

    print(table)


def process_command(user_input):
    """Разбирает и выполняет команду пользователя."""
    args = shlex.split(user_input)

    if not args:
        return True

    command = args[0].lower()
    metadata = load_metadata(META_FILE)

    if command == "exit":
        print("Выход из программы.")
        return False

    if command == "help":
        print_help()
        return True

    if command == "create_table":
        if len(args) < 3:
            raise ValueError("Укажите имя и столбцы таблицы.")

        table_name = args[1]
        result = create_table(metadata, table_name, args[2:])
        if result is None:
            return True

        save_metadata(META_FILE, result)
        save_table_data(table_name, [])
        clear_cache()
        print(f'Таблица "{table_name}" успешно создана.')
        return True

    if command == "list_tables":
        tables = list_tables(metadata)
        if not tables:
            print("Таблиц пока нет.")
        else:
            for name in tables:
                print(f"- {name}")
        return True

    if command == "drop_table":
        if len(args) != 2:
            raise ValueError("Укажите имя таблицы.")

        table_name = args[1]
        result = drop_table(metadata, table_name)
        if result is None:
            return True

        save_metadata(META_FILE, result)
        delete_table_data(table_name)
        clear_cache()

        print(f'Таблица "{table_name}" успешно удалена.')
        return True

    if command == "insert":
        match = re.fullmatch(
            r"insert\s+into\s+(\w+)\s+values\s*(\(.*\))",
            user_input,
            flags=re.IGNORECASE,
        )
        if not match:
            raise ValueError("Неверный формат insert.")

        table_name, values_text = match.groups()
        values = parse_values(values_text)
        result = insert(metadata, table_name, values)
        if result is None:
            return True

        data, record_id = result
        save_table_data(table_name, data)
        clear_cache()
        print(f'Запись с ID={record_id} добавлена в "{table_name}".')
        return True

    if command == "select":
        match = re.fullmatch(
            r"select\s+from\s+(\w+)(?:\s+where\s+(.+))?",
            user_input,
            flags=re.IGNORECASE,
        )
        if not match:
            raise ValueError("Неверный формат select.")

        table_name, condition_text = match.groups()
        check_table(metadata, table_name)
        columns = metadata[table_name]
        data = load_table_data(table_name)

        condition = None
        if condition_text:
            condition = typed_condition(condition_text, columns)

        cache_key = (
            table_name,
            str(condition),
        )

        records = cache_result(
            cache_key,
            lambda: select(data, condition),
        )

        print_records(records, columns)
        return True

    if command == "update":
        match = re.fullmatch(
            r"update\s+(\w+)\s+set\s+(.+?)\s+where\s+(.+)",
            user_input,
            flags=re.IGNORECASE,
        )
        if not match:
            raise ValueError("Неверный формат update.")

        table_name, set_text, where_text = match.groups()
        check_table(metadata, table_name)
        columns = metadata[table_name]

        set_clause = typed_condition(set_text, columns)
        where_clause = typed_condition(where_text, columns)

        if "ID" in set_clause:
            raise ValueError("Изменять ID запрещено.")

        data = load_table_data(table_name)
        data, count = update(data, set_clause, where_clause)
        save_table_data(table_name, data)
        clear_cache()
        print(f"Обновлено записей: {count}")
        return True

    if command == "delete":
        match = re.fullmatch(
            r"delete\s+from\s+(\w+)\s+where\s+(.+)",
            user_input,
            flags=re.IGNORECASE,
        )
        if not match:
            raise ValueError("Неверный формат delete.")

        table_name, where_text = match.groups()
        check_table(metadata, table_name)

        condition = typed_condition(where_text, metadata[table_name])
        data = load_table_data(table_name)

        result = delete(data, condition)
        if result is None:
            return True

        data, count = result
        save_table_data(table_name, data)
        clear_cache()

        print(f"Удалено записей: {count}")
        return True

    if command == "info":
        if len(args) != 2:
            raise ValueError("Укажите имя таблицы.")

        table_name = args[1]
        check_table(metadata, table_name)

        columns = metadata[table_name]
        data = load_table_data(table_name)

        print(f"Таблица: {table_name}")
        print(
            "Столбцы: "
            + ", ".join(f"{name}:{dtype}" for name, dtype in columns.items())
        )
        print(f"Количество записей: {len(data)}")
        return True

    print(f"Функции {command} нет. Попробуйте снова.")
    return True


def run():
    """Запускает интерактивный цикл приложения."""
    print_help()

    while True:
        try:
            user_input = input("Введите команду: ").strip()

            if not process_command(user_input):
                break

        except (ValueError, KeyError) as error:
            print(f"Ошибка: {error}")
        except EOFError:
            print("\nВыход из программы.")
            break
