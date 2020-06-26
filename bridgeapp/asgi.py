"""
Entry point to the ASGI app
---------------------------
"""

import fastapi

from . import api, settings

app = fastapi.FastAPI()

app.include_router(api.router, prefix=settings.get_settings().api_v1_prefix)
