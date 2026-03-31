# Kittygram Trips — Кото-путешествия

Расширение проекта Kittygram. Тема 23: **Кото-путешествия**.

Позволяет создавать поездки для котов, добавлять остановки маршрута, фиксировать начало и завершение путешествия.

---

## Стек

- Python 3.10
- Django 4.2
- Django REST Framework 3.15
- Djoser (авторизация по токену)
- django-filter (фильтрация)
- drf-spectacular (Swagger/Redoc)
- SQLite (для разработки)

---

## Установка и запуск

```bash
# Установить зависимости
pip install -r requirements.txt

# Скопировать файл с переменными окружения
cp .env.example .env

# Применить миграции
python manage.py migrate

# Создать суперпользователя
python manage.py createsuperuser

# Запустить сервер
python manage.py runserver
```

Репозиторий: https://github.com/Aizenhaim/kittygram_trips

После запуска доступно:
- API: http://127.0.0.1:8000/api/
- Swagger UI: http://127.0.0.1:8000/api/docs/
- Redoc: http://127.0.0.1:8000/api/redoc/
- Панель администратора: http://127.0.0.1:8000/admin/ (логин: `admin`, пароль: `admin123`)

---

## Переменные окружения (.env)

```
SECRET_KEY=ваш-секретный-ключ
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

---

## Модели

### Trip (Поездка)

| Поле | Тип | Описание |
|---|---|---|
| id | int | Первичный ключ |
| owner | FK → User | Владелец поездки |
| cat | FK → Cat | Кот-путешественник |
| title | CharField | Название поездки |
| description | TextField | Описание (необязательно) |
| status | CharField | planned / active / completed |
| started_at | DateTimeField | Дата и время начала |
| completed_at | DateTimeField | Дата и время завершения |
| created_at | DateTimeField | Дата создания (авто) |

### Stop (Остановка)

| Поле | Тип | Описание |
|---|---|---|
| id | int | Первичный ключ |
| trip | FK → Trip | Поездка |
| title | CharField | Название остановки |
| description | TextField | Описание (необязательно) |
| latitude | DecimalField | Широта (необязательно) |
| longitude | DecimalField | Долгота (необязательно) |
| order | PositiveIntegerField | Порядковый номер в маршруте |
| visited_at | DateTimeField | Время посещения (необязательно) |

---

## Бизнес-правила и валидации

1. Создавать поездку можно только для **своего** кота.
2. Нельзя добавить остановку к **завершённой** поездке.
3. Нельзя начать поездку, если её статус не `planned`.
4. Нельзя завершить поездку, если у неё нет ни одной остановки.

---

## Права доступа

| Действие | Гость | Авторизованный | Владелец |
|---|---|---|---|
| Просмотр списка поездок/остановок | ✓ | ✓ | ✓ |
| Создать поездку | — | ✓ | — |
| Редактировать / удалить поездку | — | — | ✓ |
| Начать / завершить поездку | — | — | ✓ |
| Добавить / изменить / удалить остановку | — | — | ✓ |

---

## API — таблица эндпоинтов

| Метод | URL | Права | Коды ответов | Описание |
|---|---|---|---|---|
| GET | /api/trips/ | Все | 200 | Список поездок (фильтрация + пагинация) |
| POST | /api/trips/ | Auth | 201, 400, 401 | Создать поездку |
| GET | /api/trips/{id}/ | Все | 200, 404 | Детали поездки со списком остановок |
| PATCH | /api/trips/{id}/ | Владелец | 200, 400, 403, 404 | Обновить поездку |
| DELETE | /api/trips/{id}/ | Владелец | 204, 403, 404 | Удалить поездку |
| POST | /api/trips/{id}/start/ | Auth | 200, 400, 403 | Начать поездку |
| POST | /api/trips/{id}/complete/ | Auth | 200, 400, 403 | Завершить поездку |
| GET | /api/trips/{id}/stops/ | Все | 200, 404 | Список остановок поездки |
| POST | /api/trips/{id}/stops/ | Владелец | 201, 400, 403 | Добавить остановку |
| GET | /api/trips/{id}/stops/{id}/ | Все | 200, 404 | Детали остановки |
| PATCH | /api/trips/{id}/stops/{id}/ | Владелец | 200, 400, 403 | Обновить остановку |
| DELETE | /api/trips/{id}/stops/{id}/ | Владелец | 204, 403, 404 | Удалить остановку |

---

## Фильтрация и пагинация

Эндпоинт `GET /api/trips/` поддерживает:

| Параметр | Пример | Описание |
|---|---|---|
| status | ?status=active | Фильтр по статусу |
| cat | ?cat=1 | Фильтр по ID кота |
| title | ?title=дача | Поиск по названию (частичное совпадение) |
| search | ?search=Барсик | Поиск по названию, описанию, имени кота |
| ordering | ?ordering=-created_at | Сортировка |
| page | ?page=2 | Страница (10 элементов по умолчанию) |

Примеры:
```
GET /api/trips/?status=active
GET /api/trips/?cat=1&status=planned
GET /api/trips/?title=отпуск&ordering=-created_at
GET /api/trips/?page=1
```

---

## Примеры запросов и ответов

### Получить токен

**Запрос:**
```http
POST /api/auth/token/login/
Content-Type: application/json

{
  "username": "vasilii",
  "password": "test1234"
}
```

**Ответ (200):**
```json
{
  "auth_token": "64963b4cb8ae96eb93b2a8c11e98e80223ff2fc1"
}
```

---

### Создать поездку

**Запрос:**
```http
POST /api/trips/
Authorization: Token 64963b4cb8ae96eb93b2a8c11e98e80223ff2fc1
Content-Type: application/json

{
  "cat": 1,
  "title": "Летний отпуск в Сочи",
  "description": "Первое путешествие Барсика к морю"
}
```

**Ответ (201):**
```json
{
  "id": 1,
  "owner": "vasilii",
  "cat": 1,
  "cat_name": "Барсик",
  "title": "Летний отпуск в Сочи",
  "description": "Первое путешествие Барсика к морю",
  "status": "planned",
  "started_at": null,
  "completed_at": null,
  "created_at": "2026-03-31T10:00:00+03:00",
  "stops_count": 0
}
```

**Ошибка (400) — чужой кот:**
```json
{
  "cat": ["Можно создавать поездки только для своих котов."]
}
```

---

### Начать поездку

**Запрос:**
```http
POST /api/trips/1/start/
Authorization: Token 64963b4cb8ae96eb93b2a8c11e98e80223ff2fc1
```

**Ответ (200):**
```json
{
  "id": 1,
  "status": "active",
  "started_at": "2026-03-31T10:05:00+03:00",
  ...
}
```

**Ошибка (400) — уже активна:**
```json
{
  "detail": "Нельзя начать поездку со статусом «В процессе»."
}
```

---

### Завершить поездку

**Запрос:**
```http
POST /api/trips/1/complete/
Authorization: Token 64963b4cb8ae96eb93b2a8c11e98e80223ff2fc1
```

**Ответ (200):**
```json
{
  "id": 1,
  "status": "completed",
  "completed_at": "2026-03-31T18:00:00+03:00",
  ...
}
```

**Ошибка (400) — нет остановок:**
```json
{
  "detail": "Нельзя завершить поездку без остановок."
}
```

---

### Добавить остановку

**Запрос:**
```http
POST /api/trips/1/stops/
Authorization: Token 64963b4cb8ae96eb93b2a8c11e98e80223ff2fc1
Content-Type: application/json

{
  "title": "Заправка на трассе",
  "description": "Остановка у заправки",
  "order": 1,
  "latitude": 55.800,
  "longitude": 37.650
}
```

**Ответ (201):**
```json
{
  "id": 1,
  "title": "Заправка на трассе",
  "description": "Остановка у заправки",
  "latitude": "55.800000",
  "longitude": "37.650000",
  "order": 1,
  "visited_at": null
}
```

**Ошибка (400) — завершённая поездка:**
```json
{
  "detail": "Нельзя добавлять остановки к завершённой поездке."
}
```

---

### Получить детали поездки

**Запрос:**
```http
GET /api/trips/1/
```

**Ответ (200):**
```json
{
  "id": 1,
  "owner": "vasilii",
  "cat": 1,
  "cat_name": "Барсик",
  "title": "Поездка на дачу",
  "description": "Регулярная поездка за город",
  "status": "active",
  "started_at": "2026-03-31T10:05:00+03:00",
  "completed_at": null,
  "created_at": "2026-03-31T10:00:00+03:00",
  "stops_count": 3,
  "stops": [
    {"id": 1, "title": "Заправка на трассе", "order": 1, ...},
    {"id": 2, "title": "Придорожное кафе", "order": 2, ...},
    {"id": 3, "title": "Дача", "order": 3, ...}
  ]
}
```

---

## Postman

Файл коллекции: `kittygram_trips_postman.json`

Импортировать в Postman: File → Import → выбрать файл.

Переменные коллекции:
- `base_url` = `http://127.0.0.1:8000`
- `token_vasilii` = токен пользователя vasilii
