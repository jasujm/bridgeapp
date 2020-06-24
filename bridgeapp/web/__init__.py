"""
Entry point to the ASGI app
---------------------------
"""

import fastapi

from . import api

app = fastapi.FastAPI()

app.include_router(api.router, prefix=api.ROUTER_PREFIX)
