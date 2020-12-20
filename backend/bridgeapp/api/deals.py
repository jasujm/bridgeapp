"""
Deals endpoints
...............
"""

import uuid

import fastapi

from . import models

router = fastapi.APIRouter()


@router.get(
    "/{deal_id}",
    name="deal_details",
    summary="Get infomation about a deal",
    description="""This endpoint is a stub ensuring that each deal has an URL.""",
    response_model=models.Deal,
)
def get_deal_details(request: fastapi.Request, deal_id: uuid.UUID):
    """Handle getting deal details"""
    del deal_id
    return models.Deal(self=str(request.url))
