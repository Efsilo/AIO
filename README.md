# REST API для объявлений (aiohttp)

## Запуск

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

API Endpoints

Метод URL Описание
POST /advertisement Создать
GET /advertisement/{id} Получить по ID
PATCH /advertisement/{id} Обновить
DELETE /advertisement/{id} Удалить
GET /advertisement Поиск + пагинация

Параметры поиска

· title — частичное совпадение (регистронезависимо)
· description — частичное совпадение
· price_min / price_max
· author — частичное совпадение
· skip / limit — пагинация

Примеры

```bash
curl -X POST http://localhost:8080/advertisement -H "Content-Type: application/json" -d '{"title":"iPhone","description":"Отличное состояние","price":85000,"author":"Анна"}'

curl "http://localhost:8080/advertisement?title=iphone&skip=0&limit=10"

curl -X DELETE http://localhost:8080/advertisement/{id}
```


## Запуск и тестирование

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск
python -m app.main

# В браузере
http://127.0.0.1:8080/
```

Автор

Алексеев Федор