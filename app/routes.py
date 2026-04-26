from aiohttp import web
from sqlalchemy import select
from app.database import get_db
from app.models import Advertisement
from app.schemas import AdvertisementCreate, AdvertisementUpdate, AdvertisementResponse
import json


def validate_price_range(price_min, price_max):
    if price_min is not None and price_max is not None and price_min > price_max:
        raise web.HTTPBadRequest(text=json.dumps({"detail": "price_min не может быть больше price_max"}),
                                 content_type='application/json')


async def create_advertisement(request):
    try:
        data = await request.json()
        ad_data = AdvertisementCreate(**data)

        async for db in get_db():
            new_ad = Advertisement(
                title=ad_data.title,
                description=ad_data.description,
                price=ad_data.price,
                author=ad_data.author
            )
            db.add(new_ad)
            await db.commit()
            await db.refresh(new_ad)

            response_data = AdvertisementResponse.model_validate(new_ad).model_dump()
            return web.json_response(response_data, status=201)
    except Exception as e:
        return web.json_response({"detail": "Внутренняя ошибка сервера"}, status=500)


async def get_advertisement(request):
    ad_id = request.match_info.get('advertisement_id')
    try:
        async for db in get_db():
            ad = await db.get(Advertisement, ad_id)
            if not ad:
                return web.json_response({"detail": "Объявление не найдено"}, status=404)

            response_data = AdvertisementResponse.model_validate(ad).model_dump()
            return web.json_response(response_data, status=200)
    except Exception:
        return web.json_response({"detail": "Внутренняя ошибка сервера"}, status=500)


async def update_advertisement(request):
    ad_id = request.match_info.get('advertisement_id')
    try:
        data = await request.json()
        ad_data = AdvertisementUpdate(**data)

        async for db in get_db():
            ad = await db.get(Advertisement, ad_id)
            if not ad:
                return web.json_response({"detail": "Объявление не найдено"}, status=404)

            update_data = ad_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(ad, field, value)

            await db.commit()
            await db.refresh(ad)

            response_data = AdvertisementResponse.model_validate(ad).model_dump()
            return web.json_response(response_data, status=200)
    except Exception:
        return web.json_response({"detail": "Внутренняя ошибка сервера"}, status=500)


async def delete_advertisement(request):
    ad_id = request.match_info.get('advertisement_id')
    try:
        async for db in get_db():
            ad = await db.get(Advertisement, ad_id)
            if not ad:
                return web.json_response({"detail": "Объявление не найдено"}, status=404)

            await db.delete(ad)
            await db.commit()
            return web.Response(status=204)
    except Exception:
        return web.json_response({"detail": "Внутренняя ошибка сервера"}, status=500)


async def search_advertisements(request):
    try:
        query_params = request.query

        title = query_params.get('title')
        description = query_params.get('description')
        price_min = query_params.get('price_min')
        price_max = query_params.get('price_max')
        author = query_params.get('author')
        skip = int(query_params.get('skip', 0))
        limit = int(query_params.get('limit', 100))

        if price_min is not None:
            price_min = float(price_min)
        if price_max is not None:
            price_max = float(price_max)

        validate_price_range(price_min, price_max)

        async for db in get_db():
            query = select(Advertisement)

            if title:
                query = query.where(Advertisement.title.ilike(f"%{title}%"))
            if description:
                query = query.where(Advertisement.description.ilike(f"%{description}%"))
            if price_min is not None:
                query = query.where(Advertisement.price >= price_min)
            if price_max is not None:
                query = query.where(Advertisement.price <= price_max)
            if author:
                query = query.where(Advertisement.author.ilike(f"%{author}%"))

            query = query.order_by(Advertisement.created_at.desc())
            query = query.offset(skip).limit(limit)

            result = await db.execute(query)
            ads = result.scalars().all()

            response_data = [AdvertisementResponse.model_validate(ad).model_dump() for ad in ads]
            return web.json_response(response_data, status=200)
    except web.HTTPBadRequest as e:
        return e
    except Exception:
        return web.json_response({"detail": "Внутренняя ошибка сервера"}, status=500)

async def root(request):
    return web.json_response({
        "message": "REST API для объявлений (aiohttp)",
        "endpoints": {
            "POST /advertisement": "Создать объявление",
            "GET /advertisement/{id}": "Получить объявление по ID",
            "PATCH /advertisement/{id}": "Обновить объявление",
            "DELETE /advertisement/{id}": "Удалить объявление",
            "GET /advertisement?{query_string}": "Поиск по полям с пагинацией"
        }
    })

async def favicon(request):
    return web.Response(status=204)

def setup_routes(app):
    app.router.add_get('/', root)
    app.router.add_post('/advertisement', create_advertisement)
    app.router.add_get('/advertisement/{advertisement_id}', get_advertisement)
    app.router.add_patch('/advertisement/{advertisement_id}', update_advertisement)
    app.router.add_delete('/advertisement/{advertisement_id}', delete_advertisement)
    app.router.add_get('/advertisement', search_advertisements)
    app.router.add_get('/favicon.ico', favicon)