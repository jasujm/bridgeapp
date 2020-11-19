"""
Entry point to the ASGI app
---------------------------
"""

import fastapi
import fastapi.middleware.cors

from . import api
from .settings import settings

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

application.mount(settings.api_v1_prefix, api.subapp)
