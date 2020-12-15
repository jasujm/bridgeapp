"""
Deals endpoints
...............
"""

import uuid

import fastapi

from bridgeapp.bridgeprotocol import models as base_models

router = fastapi.APIRouter()


@router.get(
    "/{deal_uuid}",
    name="deal_details",
    summary="Get infomation about a deal",
    description="""This endpoint is a stub ensuring that each deal has an URL.""",
    response_model=base_models.Deal,
)
def get_deal_details(deal_uuid: uuid.UUID):
    """Handle getting deal details"""
    return base_models.Deal(uuid=deal_uuid)
