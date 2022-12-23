# FOODGRAM
![Workflow stat](https://github.com/srgmh/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)
***
Автор: [Sergey Mankevich](https://github.com/Xewus)
***

## Технологии:

- Python 3.10
- Django 4.1.4
- Django REST Framework 3.14
- nginx
- gunicorn
- Docker
- PostgreSQL
- Github Actions
- Yandex.Cloud

***

## Описание:

Продуктовый помощник FOODGRAM представляет собой api-сервис со следующими возможностями:

- Регистрация пользователей;
- Создание, Изменение, Удаление рецептов;
- Добавление рецептов в избранное и просмотр всех избранных рецептов;
- Фильтрация рецептов по тегам;
- Подписка на авторов и просмотр рецептов определенного автора;
- Добавление рецептов и формирование списка покупок для их приготовления в формате `txt` ;

### Ссылка на API-приложение:
- http://62.84.121.139/api/

### Ссылка на фронтенд приложения:
- http://62.84.121.139/

### Ссылка на документацию по работе c API:
- http://62.84.121.139/api/docs/redoc.html

***

<details>
<summary><h2>Локальный запуск приложения:</h2></summary>

- Клонировать репозиторий на компьютер:
```
git clone https://github.com/srgmh/foodgram-project-react.git
```
- Создать виртуальное окружение:
```
python -m venv venv
```
- Перейти в виртуальное окружение:
```
source venv/bin/activate
```
- Перейти в папку `backend`
```
cd backend
```
- Установить зависимости в виртуальное окружение:
```
pip install -r requirements
```
- В файле backend/settings.py установить значение поля `POSTGRESQL_DB` на `False`. В этом случае наш проект будет работать с БД SQLite.

- Создать и выполнить миграции:
```
python manage.py makemigrations
```
```
python manage.py migrate
```
- Создать супер пользователя:
```
python manage.py createsuperuser
```
- В проекте подготовлена management команда для загрузки подготовленных данных для тегов и ингредиентов (2147 записей). Чтобы загрузить данные выполнить команду: 
```
python manage.py loaddata_tags_ingredients
```
- Запустить проект:
```
python manage.py runserver
```
***
</details>

***

<details>
<summary><h2>Запуск приложения на боевом сервере (через docker-compose):</h2></summary>

Для запуска проекта на боевом сервере понадобятся файлы из папки infra.

- Клонировать репозиторий на компьютер:
```
git clone https://github.com/srgmh/foodgram-project-react.git
```
- Подключиться к серверу:
```
ssh <server user>@<server IP>
```
- Установить Docker на сервере:
```
sudo apt install docker.io
```
- Установить docker-compose на сервер (Linux)
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```
- Предоставить права docker-compose
```
sudo chmod +x /usr/local/bin/docker-compose
```
- Создать директорию для проекта
```
mkdir foodgram && cd foodgram/
```
- Создать env-file:
```
touch .env
```
- Пример заполнения .env файла
```
DJANGO_SECRET_KEY='Django-Secret-Key'
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```
- Скопировать файлы из папки `infra` из ранее клонированного репозитория:
```
scp -r infra/* <server user>@<server IP>:/home/<server user>/foodgram/
```
- Запустить docker-compose на сервере:
```
sudo docker-compose up -d
```
- После успешной сборки контейнеров в контейнере `backend` создать и выполнить миграции, собрать статику
```
sudo docker-compose exec backend python manage.py makemigrations
sudo docker-compose exec backend python manage.py migrate
sudo docker-compose exec backend python manage.py collectstatic --no-input
```
- Создать супер пользователя:
```
sudo docker-compose exec backend python manage.py createsuperuser
```
- В проекте подготовлена management команда для загрузки подготовленных данных для тегов и ингредиентов (2147 записей). Чтобы загрузить данные выполнить команду: 
```
sudo docker-compose exec backend python manage.py loaddata_tags_ingredients
```
- Готово! Переходите на сервер, все работает.
</details>

***