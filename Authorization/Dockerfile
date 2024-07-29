# Используем официальный образ Python
FROM python:3.10

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt requirements.txt
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

# Копируем содержимое поддиректории poker_elite в /app
COPY poker_elite /app

# Открываем порт 8000 для доступа к Django
EXPOSE 8000

# Добавляем задержку в 10 секунд перед выполнением миграций и запуском сервера
CMD ["sh", "-c", "sleep 10 && python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]