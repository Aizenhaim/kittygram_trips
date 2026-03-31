# Шпаргалка — Творческое задание (тема 23)

## Проект
- Тема: Кото-путешествия (тема 23)
- Дисциплина: Интеграция и управление приложениями на удалённом сервере, РЭУ Плеханова, 2 курс
- Репозиторий: https://github.com/Aizenhaim/kittygram_trips
- Статус: ГОТОВО

## Стек
Django 4.2, DRF 3.15, Djoser, django-filter, drf-spectacular, drf-nested-routers, SQLite

## Модели
- **Trip** — поездка (owner, cat, title, description, status, started_at, completed_at)
- **Stop** — остановка маршрута (trip, title, description, latitude, longitude, order, visited_at)

## Эндпоинты
- GET/POST /api/trips/ — список/создать
- GET/PATCH/DELETE /api/trips/{id}/ — детали/редактировать/удалить
- POST /api/trips/{id}/start/ — начать поездку
- POST /api/trips/{id}/complete/ — завершить поездку
- GET/POST /api/trips/{id}/stops/ — остановки
- GET/PATCH/DELETE /api/trips/{id}/stops/{id}/ — одна остановка
- GET /api/docs/ — Swagger UI

## Валидации
1. Нельзя создать поездку для чужого кота
2. Нельзя добавить остановку к завершённой поездке
3. Нельзя начать поездку со статусом не planned
4. Нельзя завершить поездку без остановок

## Тестовые данные
- Пользователь: vasilii / test1234
- Токен: 64963b4cb8ae96eb93b2a8c11e98e80223ff2fc1
- Суперпользователь: admin / admin123
- Кот: Барсик (id=1), Мурка (id=2)
- Поездки: id=1 (planned), id=2 (active, 3 остановки)

## Запуск
```
cd "...2.Творческое задание\kittygram_trips"
.venv\Scripts\activate
python manage.py runserver
```

## Тесты
```
python manage.py test tests --verbosity=2
```
20 тестов, все проходят.

## Файлы
- `kittygram_trips_postman.json` — Postman-коллекция (14 запросов)
- `Отчёт_Кото-путешествия_тема23.docx` — Word-отчёт
- `.env.example` — шаблон переменных окружения

## Что осталось
- [ ] Скриншоты Postman → вставить в Word (раздел 8)
- [ ] Заполнить шапку Word: ФИО, группа, преподаватель

## Важно
- Не использовать слово "cloud" в коде и документах
- Это ТВОРЧЕСКОЕ задание, не путать с курсовой (папка 3.Курсовой проект)
