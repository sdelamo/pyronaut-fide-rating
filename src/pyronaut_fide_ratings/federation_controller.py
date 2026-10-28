from dataclasses import dataclass
from typing import Annotated

from jakarta.inject import Inject
from io.swagger.v3.oas.annotations import Hidden
from micronaut.data.model import Pageable
from micronaut.http import HttpResponse
from micronaut.http.annotation import Get
from micronaut.security.annotation import Secured
from micronaut.security.rules import SecurityRule
from micronaut.scheduling import TaskExecutors
from micronaut.scheduling.annotation import ExecuteOn
from micronaut.serde.annotation import Serdeable
from micronaut.views import View

from .federation import federation_flag, federation_name
from .player import PlayerRepository
from .ranking import TopPlayer, top_players

repository: Annotated[PlayerRepository, Inject]


@Serdeable
@dataclass
class FederationModel:
    """Model for the federation.jinja view."""
    name: str
    flag: str
    code: str
    period: str
    top: list[TopPlayer]


@Get("/fide/ratings/federation/{fed}")
@ExecuteOn(TaskExecutors.BLOCKING)
@Hidden
@Secured(SecurityRule.IS_ANONYMOUS)
@View("federation")
def federation(fed: str) -> HttpResponse | FederationModel:
    year = repository.findMaxRating_year()
    month = repository.findMaxRating_monthByRating_year(year) if year else None
    if not year or not month:
        return HttpResponse.notFound()
    players = repository.findByRating_yearAndRating_monthAndFedOrderByStandard_ratingDesc(year, month, fed, Pageable.from_(0, 10))
    if not players:
        return HttpResponse.notFound()
    return FederationModel(
        name=federation_name(fed),
        flag=federation_flag(fed),
        code=fed,
        period=f"{year}-{month:02d}",
        top=top_players(players),
    )
