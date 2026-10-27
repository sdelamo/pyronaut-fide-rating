from dataclasses import dataclass
from typing import Annotated

from micronaut.data.annotation import GeneratedValue, Id, MappedEntity
from micronaut.serde.annotation import Serdeable


@Serdeable
@MappedEntity("player")
@dataclass
class Player:
    fide_id: int
    rating_year: int
    rating_month: int
    name: str
    id: Annotated[int | None, Id, GeneratedValue] = None
    fed: str | None = None
    sex: str | None = None
    title: str | None = None
    w_title: str | None = None
    o_title: str | None = None
    foa: str | None = None
    standard_rating: int = 0
    standard_games: int = 0
    standard_k: int = 0
    rapid_rating: int = 0
    rapid_games: int = 0
    rapid_k: int = 0
    blitz_rating: int = 0
    blitz_games: int = 0
    blitz_k: int = 0
    birth_year: int | None = None
    flag: str | None = None
