import asyncio
import fastapi
import pytest

from bridgeapp import api, db
from bridgeapp.api import db_utils as dbu


@pytest.mark.asyncio
def test_get_player(database, client, player_id, username):
    asyncio.run(dbu.create(db.players, player_id, {"username": username}))
    res = client.get(f"/api/v1/players/{player_id}")
    assert api.models.Player(**res.json()) == api.models.Player(
        id=player_id,
        self=f"http://testserver/api/v1/players/{player_id}",
        username=username,
    )


def test_get_player_not_found(database, client, player_id):
    del database
    res = client.get(f"/api/v1/players/{player_id}")
    assert res.status_code == fastapi.status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
def test_create_player(database, client, username):
    player_create = api.models.PlayerCreate(username=username)
    res = client.post("/api/v1/players", data=player_create.json())
    assert res.status_code == fastapi.status.HTTP_201_CREATED
    player_in_response = api.models.Player(**res.json())
    player_id = player_in_response.id
    player_url = f"http://testserver/api/v1/players/{player_id}"
    assert res.headers["Location"] == player_url
    assert player_in_response == api.models.Player(
        id=player_id, self=player_url, username=username,
    )
    player_in_db = asyncio.run(
        dbu.load(db.players, player_in_response.id, database=database)
    )
    assert player_in_db == (player_id, player_in_response.username)