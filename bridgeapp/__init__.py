"""
A lightweight web application for playing contract bridge
---------------------------------------------------------
"""

from fastapi import FastAPI

from . import api

app = FastAPI()

app.include_router(api.router, prefix="/api/v1")
