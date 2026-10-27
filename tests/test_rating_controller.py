import pytest
import requests

from pyronaut.test import *
from pyronaut_fide_ratings.player import PlayerRepository

API_KEY = {"X-API-KEY": "test-key"}

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

    response = client.post("/api/v1/fide/ratings", headers=API_KEY, json=[SERGIO])

    assert response.status_code == 201
    assert response.json() == {"saved": 1, "skipped": 0}

    repository = my_context.get_bean(PlayerRepository)
    player = repository.find_latest_by_fide_id(535004274)
    assert player is not None
    assert player.name == "Del Amo Caballero, Sergio"
    assert player.standard_rating == 1598
    assert player.rating_month == 10


def test_save_ratings_skips_entries_already_imported(my_context):
    client = requests.with_context(my_context)
    client.post("/api/v1/fide/ratings", headers=API_KEY, json=[SERGIO])
    september = {**SERGIO, "rating_month": 9}

    response = client.post("/api/v1/fide/ratings", headers=API_KEY, json=[SERGIO, september])

    assert response.status_code == 201
    assert response.json() == {"saved": 1, "skipped": 1}  # October skipped, September new


def test_get_latest_rating(my_context):
    client = requests.with_context(my_context)
    september = {**SERGIO, "rating_month": 9, "standard_rating": 1590}
    client.post("/api/v1/fide/ratings", headers=API_KEY, json=[september, SERGIO])

    response = client.get("/api/v1/fide/ratings/535004274/latest")

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

    response = client.get("/api/v1/fide/ratings/1/latest")

    assert response.status_code == 404


def test_rating_profile_page(my_context):
    client = requests.with_context(my_context)
    september = {**SERGIO, "rating_month": 9, "standard_rating": 1590}
    client.post("/api/v1/fide/ratings", headers=API_KEY, json=[september, SERGIO])

    response = client.get("/fide/ratings/535004274")

    assert response.status_code == 200
    assert "text/html" in response.headers["Content-Type"]
    page = response.text
    assert "<h1>Del Amo Caballero, Sergio</h1>" in page
    assert "<dd>ESP</dd>" in page
    assert "<dd>Male</dd>" in page
    assert "<dd>1982</dd>" in page
    assert "<strong>1598</strong>" in page  # latest standard, not September's 1590
    assert "<strong>1668</strong>" in page
    assert "<strong>1610</strong>" in page
    assert "FIDE title" not in page  # Sergio has no title
    assert '<a href="/">' in page  # link back to the home page
    assert "<svg" in page and "2026-09" in page and "2026-10" in page


def test_rating_profile_page_shows_fide_title(my_context):
    client = requests.with_context(my_context)
    client.post("/api/v1/fide/ratings", headers=API_KEY, json=[{**SERGIO, "title": "IM"}])

    response = client.get("/fide/ratings/535004274")

    assert response.status_code == 200
    assert "<dt>FIDE title</dt><dd>IM</dd>" in response.text


def test_rating_profile_page_not_found(my_context):
    client = requests.with_context(my_context)

    response = client.get("/fide/ratings/1")

    assert response.status_code == 404


def test_save_ratings_requires_api_key(my_context):
    client = requests.with_context(my_context)

    assert client.post("/api/v1/fide/ratings", json=[SERGIO]).status_code == 401
    wrong = {"X-API-KEY": "wrong"}
    assert client.post("/api/v1/fide/ratings", headers=wrong, json=[SERGIO]).status_code == 401


def test_home_page_has_a_form_for_a_fide_id(my_context):
    client = requests.with_context(my_context)

    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["Content-Type"]
    assert '<form action="/fide/ratings" method="get">' in response.text
    assert 'name="fide_id"' in response.text


def test_submitting_the_form_redirects_to_the_profile(my_context):
    client = requests.with_context(my_context)

    response = client.get("/fide/ratings?fide_id=535004274", allow_redirects=False)

    assert response.status_code == 303
    assert response.headers["Location"] == "/fide/ratings/535004274"


def test_home_page_shows_the_number_of_players_in_the_latest_list(my_context):
    client = requests.with_context(my_context)
    september = {**SERGIO, "rating_month": 9}
    other = {**SERGIO, "fide_id": 1503014, "name": "Carlsen, Magnus"}
    client.post("/api/v1/fide/ratings", headers=API_KEY, json=[september, SERGIO, other])

    response = client.get("/")

    assert "<strong>2</strong> players in the 2026-10 rating list" in response.text  # September not counted


def test_home_page_without_ratings_shows_no_count(my_context):
    client = requests.with_context(my_context)

    response = client.get("/")

    assert response.status_code == 200
    assert "players in the" not in response.text


def test_home_page_lists_the_top_players_by_standard_rating(my_context):
    client = requests.with_context(my_context)
    stronger = {**SERGIO, "fide_id": 1503014, "name": "Carlsen, Magnus", "standard_rating": 2830}
    old_list = {**SERGIO, "fide_id": 2, "name": "Old Leader", "rating_month": 9, "standard_rating": 2900}
    client.post("/api/v1/fide/ratings", headers=API_KEY, json=[SERGIO, stronger, old_list])

    page = client.get("/").text

    assert "Top 10 by standard rating" in page
    assert page.index("Carlsen, Magnus") < page.index("Del Amo Caballero, Sergio")
    assert 'href="/fide/ratings/1503014"' in page
    assert "Old Leader" not in page  # only the latest list is ranked


def test_home_page_lists_federations_alphabetically_with_flags(my_context):
    client = requests.with_context(my_context)
    germany = {**SERGIO, "fide_id": 2, "name": "Player, German", "fed": "GER"}
    england = {**SERGIO, "fide_id": 3, "name": "Player, English", "fed": "ENG"}
    old_list = {**SERGIO, "fide_id": 4, "name": "Old", "fed": "FRA", "rating_month": 9}
    client.post("/api/v1/fide/ratings", headers=API_KEY, json=[SERGIO, germany, england, old_list])

    page = client.get("/").text

    assert "<h2>Federations</h2>" in page
    assert '\U0001F1EA\U0001F1F8 <a href="/fide/ratings/federation/ESP">Spain</a>' in page  # 🇪🇸
    assert '\U0001F1E9\U0001F1EA <a href="/fide/ratings/federation/GER">Germany</a>' in page  # 🇩🇪
    assert page.index(">England<") < page.index(">Germany<") < page.index(">Spain<")  # by name, not by code
    assert "federation/FRA" not in page  # only the latest list


def test_federation_page_lists_its_top_players(my_context):
    client = requests.with_context(my_context)
    spanish = {**SERGIO, "fide_id": 2, "name": "Strong, Spanish", "standard_rating": 2600}
    german = {**SERGIO, "fide_id": 3, "name": "Player, German", "fed": "GER", "standard_rating": 2700}
    client.post("/api/v1/fide/ratings", headers=API_KEY, json=[SERGIO, spanish, german])

    response = client.get("/fide/ratings/federation/ESP")

    assert response.status_code == 200
    page = response.text
    assert "<h1>\U0001F1EA\U0001F1F8 Spain</h1>" in page
    assert page.index("Strong, Spanish") < page.index("Del Amo Caballero, Sergio")
    assert 'href="/fide/ratings/2"' in page
    assert "Player, German" not in page


def test_federation_page_not_found(my_context):
    client = requests.with_context(my_context)
    client.post("/api/v1/fide/ratings", headers=API_KEY, json=[SERGIO])

    assert client.get("/fide/ratings/federation/XXX").status_code == 404


def test_style_sheet_is_served_without_an_api_key(my_context):
    client = requests.with_context(my_context)

    response = client.get("/static/styles.css")

    assert response.status_code == 200
    assert "text/css" in response.headers["Content-Type"]
    assert "font-family" in response.text


def test_pages_link_the_style_sheet(my_context):
    client = requests.with_context(my_context)
    client.post("/api/v1/fide/ratings", headers=API_KEY, json=[SERGIO])

    for path in ("/", "/fide/ratings/535004274", "/fide/ratings/federation/ESP"):
        page = client.get(path).text
        assert '<link rel="stylesheet" href="/static/styles.css">' in page
        assert "<style>" not in page
