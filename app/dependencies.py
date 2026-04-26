from aiohttp import web
from sqlalchemy import select
from app.database import get_db
from app.models import User
from app.auth import decode_token


async def get_current_user(request):
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        raise web.HTTPUnauthorized(text='{"detail": "Missing Authorization header"}', content_type='application/json')

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise web.HTTPUnauthorized(text='{"detail": "Invalid Authorization header format"}',
                                   content_type='application/json')

    token = parts[1]
    user_id = await decode_token(token)

    if not user_id:
        raise web.HTTPUnauthorized(text='{"detail": "Invalid or expired token"}', content_type='application/json')

    async for db in get_db():
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise web.HTTPUnauthorized(text='{"detail": "User not found"}', content_type='application/json')

        return user