#!/usr/bin/env bash
# exit on error
set -o errexit

# Установка продакшен зависимостей
pip install -r requirements-prod.txt

# Сборка статических файлов для продакшена
echo "Начинаем сборку статических файлов..."
python manage.py collectstatic --noinput --clear

# Проверяем, что статические файлы собраны
echo "Статические файлы собраны в: $(pwd)/staticfiles"
echo "Количество файлов: $(find staticfiles/ -type f | wc -l)"

# Применение миграций
python manage.py migrate

# === Создание суперпользователя, если он ещё не создан ===
if [[ -n "$CREATE_SUPERUSER" ]]; then
  echo "Проверка существования суперпользователя..."
  python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
username = "$DJANGO_SUPERUSER_USERNAME"
email = "$DJANGO_SUPERUSER_EMAIL"
password = "$DJANGO_SUPERUSER_PASSWORD"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print("Суперпользователь создан:", username)
else:
    print("Суперпользователь уже существует:", username)
EOF
fi
