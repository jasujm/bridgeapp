import uuid

import asyncio
import fastapi
import pytest

from bridgeapp import api, db
from bridgeapp.api import db_utils as dbu


def test_get_player(database, client, player_id, username, db_player):
    res = client.get(f"/api/v1/players/{player_id}")
    assert res.json() == {
        "id": str(player_id),
        "self": f"http://testserver/api/v1/players/{player_id}",
        "username": username,
    }


def test_nonexistent_user(client, database):
    res = client.get("/api/v1/players/me", auth=("notfound", "incorrect"))
    assert res.status_code == fastapi.status.HTTP_401_UNAUTHORIZED


def test_wrong_password(client, username, db_player):
    res = client.get("/api/v1/players/me", auth=(username, "incorrect"))
    assert res.status_code == fastapi.status.HTTP_401_UNAUTHORIZED


def test_get_self(client, credentials):
    res = client.get("/api/v1/players/me", auth=credentials)
    assert res.status_code == fastapi.status.HTTP_200_OK
    player_in_response = res.json()
    player_id = uuid.UUID(player_in_response["id"])
    assert res.json() == {
        "id": str(player_id),
        "self": f"http://testserver/api/v1/players/{player_id}",
        "username": credentials[0],
    }


def test_get_player_not_found(database, client, player_id):
    del database
    res = client.get(f"/api/v1/players/{player_id}")
    assert res.status_code == fastapi.status.HTTP_404_NOT_FOUND


def test_create_player(database, client, username, password):
    player_create = api.models.PlayerCreate(username=username, password=password)
    res = client.post("/api/v1/players", content=player_create.json())
    assert res.status_code == fastapi.status.HTTP_201_CREATED
    player_in_response = res.json()
    player_id = uuid.UUID(player_in_response["id"])
    player_url = f"http://testserver/api/v1/players/{player_id}"
    assert res.headers["Location"] == player_url
    assert player_in_response == {
        "id": str(player_id),
        "self": player_url,
        "username": username,
    }
    player_in_db = asyncio.run(dbu.load(db.players, player_id))
    assert (player_in_db.id, player_in_db.username) == (player_id, username)


def test_create_player_username_conflict(
    database, client, player_id, username, password, db_player
):
    player_create = api.models.PlayerCreate(username=username, password=password)
    res = client.post("/api/v1/players", content=player_create.json())
    assert res.status_code == fastapi.status.HTTP_409_CONFLICT


def test_change_password(client, credentials):
    new_password = "newpass"
    res = client.patch(
        "/api/v1/players/me", json={"password": new_password}, auth=credentials
    )
    assert res.status_code == fastapi.status.HTTP_204_NO_CONTENT
    res = client.get("/api/v1/players/me", auth=(credentials[0], new_password))
    assert res.status_code == fastapi.status.HTTP_200_OK
