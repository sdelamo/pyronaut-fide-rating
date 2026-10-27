from typing import Annotated

from jakarta.inject import Inject
from micronaut.http import HttpStatus
from micronaut.http.annotation import Body, Get, Post, Status

from .player import Player
from .player_repository import PlayerRepository

repository: Annotated[PlayerRepository, Inject]


@Post("/api/v1/fide/ratings")
@Status(HttpStatus.CREATED)
def save_ratings(players: Annotated[list[Player], Body]) -> dict[str, int]:
    for player in players:
        repository.save(player)
    return {"saved": len(players)}


@Get("/api/v1/fide/ratings/{fide_id}")
def latest_rating(fide_id: int) -> Player | None:
    return repository.find_latest_by_fide_id(fide_id)
