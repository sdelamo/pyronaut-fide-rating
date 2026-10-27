from typing import Annotated

from jakarta.inject import Inject
from io.swagger.v3.oas.annotations import Hidden, Operation
from io.swagger.v3.oas.annotations.responses import ApiResponse
from io.swagger.v3.oas.annotations.security import SecurityRequirement
from micronaut.http import HttpResponse, HttpStatus
from micronaut.http.annotation import Body, Get, Post, Status
from micronaut.security.annotation import Secured
from micronaut.security.rules import SecurityRule
from micronaut.views import View

from .player import Player, PlayerRepository
from .rating_chart import ProfileModel, profile_model

repository: Annotated[PlayerRepository, Inject]


@Post("/api/v1/fide/ratings")
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
        if repository.count_by_fide_id_and_period(player.fide_id, player.rating_year, player.rating_month) == 0:
            repository.save(player)
            saved += 1
    return {"saved": saved, "skipped": len(players) - saved}


@Get("/api/v1/fide/ratings/{fide_id}/latest")
@Secured(SecurityRule.IS_ANONYMOUS)
def latest_rating(fide_id: int) -> Player | None:
    return repository.find_latest_by_fide_id(fide_id)


@Get("/fide/ratings/{fide_id}")
@Hidden
@Secured(SecurityRule.IS_ANONYMOUS)
@View("profile")
def rating_profile(fide_id: int) -> HttpResponse | ProfileModel:
    history = repository.find_all_by_fide_id(fide_id)
    if not history:
        return HttpResponse.notFound()
    return profile_model(history)
