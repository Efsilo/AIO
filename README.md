# REST API для объявлений (aiohttp + JWT)

## Технологии
- Python 3.11
- aiohttp
- SQLAlchemy (асинхронный)
- SQLite
- JWT (python-jose)
- bcrypt (passlib)
- Docker

## Установка и запуск

### Локально
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m app.main
```

Docker

```bash
docker build -t aiohttp-ads .
docker run -p 8080:8080 aiohttp-ads
```

Примеры запросов

1. Регистрация

```bash
curl -X POST http://localhost:8080/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secret123"}'
```

2. Логин (получение токена)

```bash
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secret123"}'
```

3. Создание объявления (с токеном)

```bash
curl -X POST http://localhost:8080/advertisement \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"title":"MacBook Pro","description":"16GB RAM","price":150000}'
```

4. Получение объявления

```bash
curl http://localhost:8080/advertisement/ID
```

5. Обновление (только владелец)

```bash
curl -X PATCH http://localhost:8080/advertisement/ID \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"price":140000}'
```

6. Удаление (только владелец)

```bash
curl -X DELETE http://localhost:8080/advertisement/ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

7. Поиск с пагинацией

```bash
curl "http://localhost:8080/advertisement?title=macbook&price_min=100000&skip=0&limit=10"
```


Структура проекта

```
aiohttp/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   ├── routes.py
│   ├── auth.py
│   └── dependencies.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore
└── README.md
```

```
Автор

Алексеев Федор