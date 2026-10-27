import pytest
import requests

from pyronaut.test import *
from pyronaut_fide_ratings.player_repository import PlayerRepository

# Sergio del Amo's entry from the FIDE list (October 2026)
SERGIO = {
    "fide_id": 535004274,
    "rating_year": 2026,
    "rating_month": 10,
    "name": "Del Amo Caballero, Sergio",
    "fed": "ESP",
    "sex": "M",
    "standard_rating": 1598,
    "standard_games": 0,
    "standard_k": 40,
    "rapid_rating": 1668,
    "rapid_games": 0,
    "rapid_k": 40,
    "blitz_rating": 1610,
    "blitz_games": 0,
    "blitz_k": 20,
    "birth_year": 1982,
}


@pytest.fixture
def my_context(request):
    fixture = micronaut_test_fixture(
        request, MicronautTest(environments=["test"], transactional=False)
    )
    yield fixture
    fixture.stop()


def test_save_ratings(my_context):
    client = requests.with_context(my_context)

    response = client.post("/api/v1/fide/ratings", json=[SERGIO])

    assert response.status_code == 201
    assert response.json() == {"saved": 1}

    repository = my_context.get_bean(PlayerRepository)
    player = repository.find_latest_by_fide_id(535004274)
    assert player is not None
    assert player.name == "Del Amo Caballero, Sergio"
    assert player.standard_rating == 1598
    assert player.rating_month == 10


def test_get_latest_rating(my_context):
    client = requests.with_context(my_context)
    september = {**SERGIO, "rating_month": 9, "standard_rating": 1590}
    client.post("/api/v1/fide/ratings", json=[september, SERGIO])

    response = client.get("/api/v1/fide/ratings/535004274")

    assert response.status_code == 200
    player = response.json()
    assert player["fide_id"] == 535004274
    assert player["name"] == "Del Amo Caballero, Sergio"
    assert (player["rating_year"], player["rating_month"]) == (2026, 10)
    assert player["standard_rating"] == 1598
    assert player["rapid_rating"] == 1668
    assert player["blitz_rating"] == 1610


def test_get_latest_rating_not_found(my_context):
    client = requests.with_context(my_context)

    response = client.get("/api/v1/fide/ratings/1")

    assert response.status_code == 404
