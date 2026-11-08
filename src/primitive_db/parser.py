"""Разбор пользовательских команд."""

import shlex


def parse_values(text):
    """Разбирает значения в скобках."""
    text = text.strip()

    if not text.startswith("(") or not text.endswith(")"):
        raise ValueError("Значения должны быть в скобках.")

    text = text[1:-1]
    lexer = shlex.shlex(text, posix=False)
    lexer.whitespace = ","
    lexer.whitespace_split = True

    return [value.strip().strip('"').strip("'") for value in lexer]


def parse_condition(text):
    """Преобразует условие в словарь."""
    if "=" not in text:
        raise ValueError("Условие должно содержать знак =.")

    column, value = text.split("=", 1)
    column = column.strip()
    value = value.strip().strip('"').strip("'")

    if not column:
        raise ValueError("Не указан столбец.")

    if value.lower() == "true":
        value = True
    elif value.lower() == "false":
        value = False
    else:
        try:
            value = int(value)
        except ValueError:
            pass

    return {column: value}
