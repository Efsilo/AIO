from aiohttp import web
from app.routes import setup_routes
from app.database import engine, Base
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def make_app():
    await init_db()
    app = web.Application()
    setup_routes(app)
    return app

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = loop.run_until_complete(make_app())
    web.run_app(app, host='127.0.0.1', port=8080)