# api_yamdb - API для проекта YaMDb

![yamdb workflow](https://github.com/sofyaserpinskaya/yamdb_final/workflows/yamdb_workflow/badge.svg)

## Описание

Проект YaMDb собирает отзывы пользователей на различные произведения (фильмы, книги, музыка).

### Команда разработчиков

[Софья Серпинская](https://github.com/sofyaserpinskaya) - лид команды, реализация review, comments, управления пользователями

[Сергей Поляков](https://github.com/SergeyPolyakov87) - реализация categories, genres, titles

[Динара Фатехова](https://github.com/Dinara-F) - регистрация пользователей

### Технологии

Python, Django, PostgreSQL, Simple JWT, git

### Шаблон наполнения env-файла

```bash
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
DB_HOST=db
DB_PORT=5432
SECRET_KEY=secretkey
```

### Запуск приложения в контейнерах

Запуск docker-compose:

```bash
docker-compose up -d
```

Выполнить миграции:

```bash
docker-compose exec web python manage.py migrate
```

Создать суперюзера:

```bash
docker-compose exec web python manage.py createsuperuser
```

Собрать статику:

```bash
docker-compose exec web python manage.py collectstatic --no-input
```

### Заполнение базы данными

```bash
docker-compose exec web python manage.py loaddata fixtures.json
```
