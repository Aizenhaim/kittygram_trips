# Docker — шпаргалка

## Основные команды

### Запуск проекта
```bash
docker-compose up --build
```
Пересобрать образы и запустить все контейнеры. Используй при первом запуске или после изменений в Dockerfile/requirements.txt.

```bash
docker-compose up
```
Запустить без пересборки (быстрее, если код не менялся).

```bash
docker-compose up -d
```
Запустить в фоне (detached mode). Терминал не занят.

---

### Остановка

```bash
docker-compose down
```
Остановить и удалить контейнеры. Данные в томах (volumes) сохраняются.

```bash
docker-compose down -v
```
Остановить и удалить контейнеры **вместе с томами** (база данных будет удалена). Используй если нужен чистый старт.

---

### Просмотр логов

```bash
docker-compose logs
```
Показать все логи всех сервисов.

```bash
docker-compose logs backend
```
Логи конкретного сервиса (backend / db / gateway / frontend).

```bash
docker-compose logs -f backend
```
Следить за логами в реальном времени (`-f` = follow).

---

### Статус контейнеров

```bash
docker-compose ps
```
Список запущенных контейнеров и их статус (running / exited).

---

### Выполнение команд внутри контейнера

```bash
docker-compose exec backend bash
```
Открыть bash-оболочку внутри контейнера backend.

```bash
docker-compose exec backend python manage.py createsuperuser
```
Создать суперпользователя Django.

```bash
docker-compose exec backend python manage.py shell
```
Открыть Django shell (для отладки и тестовых данных).

```bash
docker-compose exec backend python manage.py migrate
```
Применить миграции вручную (обычно запускается автоматически при старте).

---

### Пересборка одного сервиса

```bash
docker-compose build backend
```
Пересобрать только образ backend (не поднимает контейнер).

```bash
docker-compose up -d --no-deps --build backend
```
Пересобрать и перезапустить только backend, не трогая остальные контейнеры.

---

### Очистка

```bash
docker builder prune -f
```
Удалить кеш сборки. Помогает при ошибках типа "snapshot does not exist".

```bash
docker system prune -f
```
Удалить всё неиспользуемое: остановленные контейнеры, образы без тегов, кеш сборки.

```bash
docker system prune -af
```
То же самое, но удаляет и неиспользуемые образы с тегами. Освобождает максимум места.

---

## Типичные сценарии

| Ситуация | Команда |
|----------|---------|
| Первый запуск | `docker-compose up --build` |
| Изменил Python-код | `docker-compose up -d --no-deps --build backend` |
| Изменил nginx.conf | `docker-compose restart gateway` |
| Нужен чистый старт (снести БД) | `docker-compose down -v && docker-compose up --build` |
| Ошибка кеша сборки | `docker builder prune -f && docker-compose up --build` |
| Создать суперпользователя | `docker-compose exec backend python manage.py createsuperuser` |
| Посмотреть что происходит | `docker-compose logs -f` |
