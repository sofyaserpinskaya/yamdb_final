# api_yamdb

![yamdb workflow](https://github.com/sofyaserpinskaya/yamdb_final/workflows/yamdb_workflow/badge.svg)

## Описание

Проект YaMDb собирает отзывы пользователей на различные произведения.

### Команда разработчиков

Софья Серпинская <https://github.com/sofyaserpinskaya>

Сергей Поляков <https://github.com/SergeyPolyakov87>

Динара Фатехова <https://github.com/Dinara-F>

### Технологии

```bash
Django==2.2.16
django-filter==21.1
djangorestframework==3.12.4
djangorestframework-simplejwt==5.0.0
```

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

### Развернутый проект

<http://51.250.104.165/api/v1/>

### Документация API-сервера

<http://51.250.104.165/redoc/>
