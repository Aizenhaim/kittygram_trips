FROM python:3.10-slim

WORKDIR /app

RUN pip install gunicorn==20.1.0

COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --no-input && python manage.py shell -c \"from django.contrib.auth import get_user_model; U = get_user_model(); U.objects.filter(username='admin').exists() or U.objects.create_superuser('admin', 'admin@example.com', 'admin123'); U.objects.filter(username='vasilii').exists() or U.objects.create_user('vasilii', 'vasilii@example.com', 'test1234')\" && gunicorn --bind 0.0.0.0:8000 kittygram_trips.wsgi"]
