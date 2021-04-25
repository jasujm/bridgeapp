"""
Deals endpoints
...............
"""

import uuid

import fastapi

from . import models, utils

router = fastapi.APIRouter()


@router.get(
    "/{deal_id}",
    name="deal_details",
    summary="Get infomation about a deal",
    description="""The response contains the representation of the deal. If the deal is ongoing,
    only public state is included (so no hidden cards or tricks). If the deal
    has ended, the response contains a full description of the deal (including
    all hands and tricks).""",
    response_model=models.Deal,
    responses={
        fastapi.status.HTTP_404_NOT_FOUND: {
            "model": models.Error,
            "description": "Deal not found",
        }
    },
)
async def get_deal_details(request: fastapi.Request, deal_id: uuid.UUID):
    """Handle getting deal details"""
    client = await utils.get_bridge_client()
    deal = await client.get_deal(deal=deal_id)
    return models.Deal.from_attributes(deal, request)
