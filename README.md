# FoodGram

FoodGram — это образовательный проект, созданный во время обучения в Яндекс Практикуме.
Он позволяет пользователям создавать, хранить и делиться рецептами онлайн.
Также можно скачивать список продуктов, просматривать рецепты друзей и добавлять любимые блюда в избранное.

Ознакомится можно тут: https://foodgrampro.hopto.org/recipes

Автор - [Khalin Vadim](https://t.me/gohub1)

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
- Python 3.12
- Django 5.2.8
- Django REST Framework 3.16.1
- Djoser 2.3.3
- PostgreSQL 16
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
