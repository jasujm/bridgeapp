"""
Entry point to the ASGI app
---------------------------
"""

import fastapi
import fastapi.middleware.cors
import hrefs.starlette

from . import api
from .settings import settings
from .db import database

application = fastapi.FastAPI()

# Allow cross-origin references for development

origins = [
    "http://localhost",
    "http://localhost:8080",
]

application.add_middleware(
    fastapi.middleware.cors.CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[api.games.COUNTER_HEADER],
)

application.add_middleware(hrefs.starlette.HrefMiddleware)

application.mount(settings.api_v1_prefix, api.subapp)


@application.on_event("startup")
async def startup():
    """Startup task"""
    await database.connect()


@application.on_event("shutdown")
async def shutdown():
    """Shutdown task"""
    await database.disconnect()
