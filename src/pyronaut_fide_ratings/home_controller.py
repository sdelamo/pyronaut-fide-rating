from dataclasses import dataclass
from typing import Annotated

from jakarta.inject import Inject
from io.swagger.v3.oas.annotations import Hidden
from java.net import URI
from micronaut.data.model import Pageable
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
    """Model for the home.jinja view: the latest rating list (players and period are None before any import)."""
    players: str | None
    period: str | None
    top: list[TopPlayer]
    federations: list[FederationLink]


@Get("/")
@Hidden
@Secured(SecurityRule.IS_ANONYMOUS)
@View("home")
def home() -> HomeModel:
    year = repository.findMaxRating_year()
    month = repository.findMaxRating_monthByRating_year(year) if year else None
    if not year or not month:
        return HomeModel(players=None, period=None, top=[], federations=[])
    federations = [
        FederationLink(f"/fide/ratings/federation/{code}", federation_flag(code), federation_name(code), code)
        for code in repository.findDistinctFedByRating_yearAndRating_monthAndFedIsNotNull(year, month)
    ]
    federations.sort(key=lambda federation: federation.name.lower())
    return HomeModel(
        players=f"{repository.countByRating_yearAndRating_month(year, month):,}",
        period=f"{year}-{month:02d}",
        top=top_players(repository.findByRating_yearAndRating_monthOrderByStandard_ratingDesc(year, month, Pageable.from_(0, 10))),
        federations=federations,
    )
