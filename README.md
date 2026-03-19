# FoodGram
![Foodgram](https://github.com/GohubSilently/foodgram/actions/workflows/main.yml/badge.svg)

FoodGram — cервис позволяющий пользователям создавать, хранить и делиться рецептами онлайн.
Также можно скачивать список продуктов, просматривать рецепты друзей и добавлять любимые блюда в избранное.

Ознакомится можно тут: [FoodGram](https://foodgrampro.hopto.org/recipes)

Админ Зона: [Admin](https://foodgrampro.hopto.org/recipes/admin/)

Документация API: [API](https://foodgrampro.hopto.org/api/docs/)

Автор - [Халин Вадим](https://t.me/gohub1)

---
## Возможности

- Регистрация и авторизация пользователей  
- Создание и редактирование рецептов  
- Список избранных рецептов  
- Скачивание списка ингредиентов для рецепта  
- Просмотр рецептов других пользователей  

---
## Технологии

### Основные технологии и версии
- Python
- Django
- Django REST Framework
- Djoser
- PostgreSQL - для продакшена
- SQLite - для локальной разработки
- Docker, Docker Compose
- Nginx

### Основные навыки
- REST API и аутентификация через JWT
- Работа с базой данных PostgreSQL
- Развёртывание через Docker и Nginx
- Обработка изображений с Pillow

---

## Установка

1. Клонируем репозиторий:
```
git clone git@github.com:GohubSilently/foodgram.git
cd foodgram
```

2. Создаем .env
```
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=securepassword
DEBUG=False
SECRET_KEY=your_secret_key
ALLOWED_HOSTS=localhost 127.0.0.1
```

3. Заупускаем проект
```
docker compose down && docker compose up --build
```

4. Загружаем данные и применяем миграции
```
docker compose exec foodgram_backend python manage.py migrate
docker compose exec foodgram_backend python manage.py collectstatic
docker compose exec foodgram_backend cp -r /app/collected_static/. /backend_static/
docker compose exec foodgram_backend python manage.py load_ingredients ./appp/backend/data/ingredients.json
docker compose exec foodgram_backend python manage.py load_tags ./appp/backend/data/tags.json
```

5. Запустить проект докально
```
git clone git@github.com:GohubSilently/foodgram.git
cd backend && python3 -m venv venv && source venv/bin/activate
python manage.py migrate
python manage.py load_ingredients
python manage.py load_tags
```
