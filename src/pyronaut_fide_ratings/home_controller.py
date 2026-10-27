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

from .federation import federation_flag, federation_name
from .player import PlayerRepository
from .ranking import TopPlayer, top_players

repository: Annotated[PlayerRepository, Inject]


@Serdeable
@dataclass
class FederationLink:
    link: str  # the template can't read snake_case properties of nested items
    flag: str
    name: str
    code: str


@Serdeable
@dataclass
class HomeModel:
    """Model for the home.jinja view: the latest rating list (empty before any import)."""
    players: str
    period: str
    top: list[TopPlayer]
    federations: list[FederationLink]


@Get("/")
@Secured(SecurityRule.IS_ANONYMOUS)
@View("home")
def home() -> HomeModel:
    year = repository.find_latest_rating_year()
    month = repository.find_latest_rating_month(year) if year else None
    if not year or not month:
        return HomeModel(players="", period="", top=[], federations=[])
    federations = [
        FederationLink(f"/fide/ratings/federation/{code}", federation_flag(code), federation_name(code), code)
        for code in repository.find_federations(year, month)
    ]
    federations.sort(key=lambda federation: federation.name.lower())
    return HomeModel(
        players=f"{repository.count_by_period(year, month):,}",
        period=f"{year}-{month:02d}",
        top=top_players(repository.find_top_by_standard_rating(year, month, 10)),
        federations=federations,
    )


# A GET form can only submit a query string, so this turns ?fide_id=... into the path URL
@Get("/fide/ratings")
@Secured(SecurityRule.IS_ANONYMOUS)
def search(fide_id: int) -> HttpResponse:
    return HttpResponse.seeOther(URI.create(f"/fide/ratings/{fide_id}"))
