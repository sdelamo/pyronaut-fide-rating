from typing import Annotated

from jakarta.inject import Inject
from io.swagger.v3.oas.annotations import Hidden, Operation
from io.swagger.v3.oas.annotations.responses import ApiResponse
from io.swagger.v3.oas.annotations.security import SecurityRequirement
from java.net import URI
from micronaut.http import HttpResponse, HttpStatus
from micronaut.http.annotation import Body, Get, Post, Status
from micronaut.security.annotation import Secured
from micronaut.security.rules import SecurityRule
from micronaut.scheduling import TaskExecutors
from micronaut.scheduling.annotation import ExecuteOn
from micronaut.views import View

from .player import Player, PlayerRepository
from .rating_chart import ProfileModel, profile_model

repository: Annotated[PlayerRepository, Inject]


@Post("/api/v1/fide/ratings")
@ExecuteOn(TaskExecutors.BLOCKING)
@Operation(
    summary="Save the ratings of a rating list",
    description="Entries already stored for the same FIDE ID, year and month are skipped, so a list can be re-imported.",
    security=[SecurityRequirement(name="apiKey")],
)
@ApiResponse(responseCode="401", description="The X-API-KEY header is missing or wrong")
@Secured(SecurityRule.IS_AUTHENTICATED)
@Status(HttpStatus.CREATED)
def save_ratings(players: Annotated[list[Player], Body]) -> dict[str, int]:
    saved = 0
    for player in players:
        # re-importing a list must not fail: skip what is already stored
        if repository.countByFide_idAndRating_yearAndRating_month(player.fide_id, player.rating_year, player.rating_month) == 0:
            repository.save(player)
            saved += 1
    return {"saved": saved, "skipped": len(players) - saved}


@Get("/api/v1/fide/ratings/{fide_id}/latest")
@ExecuteOn(TaskExecutors.BLOCKING)
@Secured(SecurityRule.IS_ANONYMOUS)
def latest_rating(fide_id: int) -> Player | None:
    return repository.findFirstByFide_idOrderByRating_yearDescAndRating_monthDesc(fide_id)


@Get("/fide/ratings/{fide_id}")
@ExecuteOn(TaskExecutors.BLOCKING)
@Hidden
@Secured(SecurityRule.IS_ANONYMOUS)
@View("profile")
def rating_profile(fide_id: int) -> HttpResponse | ProfileModel:
    history = repository.findByFide_idOrderByRating_yearAscAndRating_monthAsc(fide_id)
    if not history:
        return HttpResponse.notFound()
    return profile_model(history)


# A GET form can only submit a query string, so this turns ?fide_id=... into the path URL
@Get("/fide/ratings")
@Hidden
@Secured(SecurityRule.IS_ANONYMOUS)
def search(fide_id: int) -> HttpResponse:
    return HttpResponse.seeOther(URI.create(f"/fide/ratings/{fide_id}"))
