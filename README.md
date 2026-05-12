# Online Store

Интернет-магазин на Django.

## Функциональность

- Django проект
- Приложение catalog
- Главная страница
- Страница контактов
- Bootstrap интерфейс
- GET запросы
- POST запросы
- Обработка формы
- Вывод данных формы в консоль
- PostgreSQL
- ORM Django
- Модели Category и Product
- Django admin
- CRUD операции через ORM
- Миграции
- Медиафайлы
- Переменные окружения (.env)
- Фикстуры
- Кастомная management-команда fill

## Установка
```
git clone https://github.com/almsar99/online-store.git
```
## Создание виртуального окружения:
```
python3 -m venv venv
source venv/bin/activate
```
## Установка зависимостей:
```
pip install -r requirements.txt
```
## Запуск проекта:
```
python manage.py runserver
```
## Открыть в браузере:
```
http://127.0.0.1:8000/
```
## Миграции
```
python manage.py makemigrations
python manage.py migrate
```

## Создание суперпользователя
```
python manage.py createsuperuser
```

## Загрузка фикстур
```
python manage.py fill
```

## Скриншоты
Скриншоты ORM-запросов находятся в папке screenshots
