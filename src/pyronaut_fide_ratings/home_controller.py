from dataclasses import dataclass
from typing import Annotated

from jakarta.inject import Inject
from java.net import URI
from micronaut.http import HttpResponse
from micronaut.http.annotation import Get
from micronaut.security.annotation import Secured
from micronaut.security.rules import SecurityRule
from micronaut.serde.annotation import Serdeable
from micronaut.views import View

from .player import PlayerRepository

repository: Annotated[PlayerRepository, Inject]


@Serdeable
@dataclass
class HomeModel:
    """Model for the home.jinja view: the size of the latest rating list (empty before any import)."""
    players: str
    period: str


@Get("/")
@Secured(SecurityRule.IS_ANONYMOUS)
@View("home")
def home() -> HomeModel:
    year = repository.find_latest_rating_year()
    month = repository.find_latest_rating_month(year) if year else None
    if not year or not month:
        return HomeModel(players="", period="")
    return HomeModel(
        players=f"{repository.count_by_period(year, month):,}",
        period=f"{year}-{month:02d}",
    )


# A GET form can only submit a query string, so this turns ?fide_id=... into the path URL
@Get("/fide/ratings")
@Secured(SecurityRule.IS_ANONYMOUS)
def search(fide_id: int) -> HttpResponse:
    return HttpResponse.seeOther(URI.create(f"/fide/ratings/{fide_id}"))
