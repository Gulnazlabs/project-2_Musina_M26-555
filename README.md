# Примитивная база данных

Учебный проект на Python - консольное приложение для управления простой базой данных с хранением информации в JSON-файлах.

## Возможности

- Создание и удаление таблиц
- Просмотр списка таблиц и их структуры
- Добавление записей
- Поиск и просмотр записей
- Изменение и удаление записей
- Поддержка типов `int`, `str`, `bool`
- Автоматическое присвоение ID
- Подтверждение операций удаления
- Измерение времени выполнения функций
- Кэширование результатов запросов
- Обработка ошибок

## Технологии

- Python 3.12
- uv
- PrettyTable
- Ruff
- Git

## Установка

Клонировать репозиторий:

```bash
git clone https://github.com/Gulnazlabs/project-2_Musina_M26-555.git
```

Перейти в папку проекта:

```bash
cd project-2_Musina_M26-555
```

Установить зависимости:

```bash
uv sync
```

## Запуск

```bash
uv run database
```

## Примеры команд

Создание таблицы:

```text
create_table users name:str age:int is_active:bool
```

Добавление записей:

```text
insert into users values ("Anna", 25, true)
insert into users values ("Maria", 30, false)
```

Просмотр записей:

```text
select from users
```

Поиск:

```text
select from users where age = 25
```

Обновление:

```text
update users set age = 26 where name = "Anna"
```

Удаление записи:

```text
delete from users where ID = 2
```

Информация о таблице:

```text
info users
```

Удаление таблицы:

```text
drop_table users
```

Выход:

```text
exit
```

## Проверка качества кода

```bash
uv run ruff check .
uv run ruff format --check .
```

## Структура проекта

```text
src/primitive_db/
    __init__.py
    main.py
    engine.py
    core.py
    parser.py
    utils.py
    decorators.py
    constants.py
```

## Хранение данных

Структура таблиц хранится в `db_meta.json`, записи - в отдельных JSON-файлах папки `data/`.


## Демонстрация работы программы

Запись работы консольной базы данных с помощью asciinema.

[Посмотреть демонстрацию](https://asciinema.org/a/aqfckVZyKBm0LdrQ)


## Автор

Мусина, группа М26-555.
