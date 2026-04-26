from aiohttp import web
from sqlalchemy import select
from datetime import timedelta
import json

from app.database import get_db
from app.models import User, Advertisement
from app.schemas import UserRegister, UserLogin, AdvertisementCreate, AdvertisementUpdate, AdvertisementResponse
from app.auth import verify_password, get_password_hash, create_access_token
from app.dependencies import get_current_user


def validate_price_range(price_min, price_max):
    if price_min is not None and price_max is not None and price_min > price_max:
        raise web.HTTPBadRequest(text=json.dumps({"detail": "price_min cannot be greater than price_max"}),
                                 content_type='application/json')


async def register(request):
    try:
        data = await request.json()
        user_data = UserRegister(**data)

        async for db in get_db():
            result = await db.execute(select(User).where(User.email == user_data.email))
            existing = result.scalar_one_or_none()
            if existing:
                return web.json_response({"detail": "Email already registered"}, status=400)

            hashed_password = get_password_hash(user_data.password)
            new_user = User(
                email=user_data.email,
                password_hash=hashed_password
            )
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)

            return web.json_response({"id": new_user.id, "email": new_user.email}, status=201)
    except Exception as e:
        return web.json_response({"detail": str(e)}, status=400)


async def login(request):
    try:
        data = await request.json()
        login_data = UserLogin(**data)

        async for db in get_db():
            result = await db.execute(select(User).where(User.email == login_data.email))
            user = result.scalar_one_or_none()

            if not user or not verify_password(login_data.password, user.password_hash):
                return web.json_response({"detail": "Invalid email or password"}, status=401)

            access_token = create_access_token(data={"sub": user.id}, expires_delta=timedelta(minutes=30))
            return web.json_response({"access_token": access_token, "token_type": "bearer"}, status=200)
    except Exception as e:
        return web.json_response({"detail": str(e)}, status=400)


async def create_advertisement(request):
    try:
        user = await get_current_user(request)
        data = await request.json()
        ad_data = AdvertisementCreate(**data)

        async for db in get_db():
            new_ad = Advertisement(
                title=ad_data.title,
                description=ad_data.description,
                price=ad_data.price,
                user_id=user.id
            )
            db.add(new_ad)
            await db.commit()
            await db.refresh(new_ad)

            return web.json_response(AdvertisementResponse.model_validate(new_ad).model_dump(), status=201)
    except web.HTTPException:
        raise
    except Exception as e:
        return web.json_response({"detail": "Internal server error"}, status=500)


async def get_advertisement(request):
    ad_id = request.match_info.get('advertisement_id')
    try:
        async for db in get_db():
            ad = await db.get(Advertisement, ad_id)
            if not ad:
                return web.json_response({"detail": "Advertisement not found"}, status=404)

            return web.json_response(AdvertisementResponse.model_validate(ad).model_dump(), status=200)
    except Exception:
        return web.json_response({"detail": "Internal server error"}, status=500)


async def update_advertisement(request):
    ad_id = request.match_info.get('advertisement_id')
    try:
        user = await get_current_user(request)
        data = await request.json()
        ad_data = AdvertisementUpdate(**data)

        async for db in get_db():
            ad = await db.get(Advertisement, ad_id)
            if not ad:
                return web.json_response({"detail": "Advertisement not found"}, status=404)

            if ad.user_id != user.id:
                return web.json_response({"detail": "Not enough permissions"}, status=403)

            update_data = ad_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(ad, field, value)

            await db.commit()
            await db.refresh(ad)

            return web.json_response(AdvertisementResponse.model_validate(ad).model_dump(), status=200)
    except web.HTTPException:
        raise
    except Exception:
        return web.json_response({"detail": "Internal server error"}, status=500)


async def delete_advertisement(request):
    ad_id = request.match_info.get('advertisement_id')
    try:
        user = await get_current_user(request)

        async for db in get_db():
            ad = await db.get(Advertisement, ad_id)
            if not ad:
                return web.json_response({"detail": "Advertisement not found"}, status=404)

            if ad.user_id != user.id:
                return web.json_response({"detail": "Not enough permissions"}, status=403)

            await db.delete(ad)
            await db.commit()
            return web.Response(status=204)
    except web.HTTPException:
        raise
    except Exception:
        return web.json_response({"detail": "Internal server error"}, status=500)


async def search_advertisements(request):
    try:
        query_params = request.query

        title = query_params.get('title')
        description = query_params.get('description')
        price_min = query_params.get('price_min')
        price_max = query_params.get('price_max')
        author_id = query_params.get('user_id')
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
            if author_id:
                query = query.where(Advertisement.user_id == author_id)

            query = query.order_by(Advertisement.created_at.desc())
            query = query.offset(skip).limit(limit)

            result = await db.execute(query)
            ads = result.scalars().all()

            return web.json_response([AdvertisementResponse.model_validate(ad).model_dump() for ad in ads], status=200)
    except web.HTTPBadRequest as e:
        return e
    except Exception:
        return web.json_response({"detail": "Internal server error"}, status=500)


async def root(request):
    return web.json_response({
        "message": "REST API for advertisements",
        "endpoints": {
            "POST /auth/register": "Register user",
            "POST /auth/login": "Login, get JWT token",
            "POST /advertisement": "Create advertisement (requires JWT)",
            "GET /advertisement/{id}": "Get advertisement by ID",
            "PATCH /advertisement/{id}": "Update advertisement (owner only)",
            "DELETE /advertisement/{id}": "Delete advertisement (owner only)",
            "GET /advertisement": "Search with pagination"
        }
    })


def setup_routes(app):
    app.router.add_get('/', root)
    app.router.add_post('/auth/register', register)
    app.router.add_post('/auth/login', login)
    app.router.add_post('/advertisement', create_advertisement)
    app.router.add_get('/advertisement/{advertisement_id}', get_advertisement)
    app.router.add_patch('/advertisement/{advertisement_id}', update_advertisement)
    app.router.add_delete('/advertisement/{advertisement_id}', delete_advertisement)
    app.router.add_get('/advertisement', search_advertisements)