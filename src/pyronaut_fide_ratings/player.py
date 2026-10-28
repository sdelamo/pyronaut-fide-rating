from dataclasses import dataclass
from typing import Annotated

from micronaut.data.annotation import GeneratedValue, Id, MappedEntity
from micronaut.data.jdbc.annotation import JdbcRepository
from micronaut.data.model import Pageable
from micronaut.data.model.query.builder.sql import Dialect
from micronaut.data.repository import CrudRepository
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


@JdbcRepository(dialect=Dialect.SQLITE)
class PlayerRepository(CrudRepository[Player, int]):
    """Micronaut Data derives each query from the method name, which spells the entity's snake_case properties."""

    def findByFide_idAndRating_yearAndRating_month(
        self, fide_id: int, rating_year: int, rating_month: int
    ) -> Player | None: ...

    def findFirstByFide_idOrderByRating_yearDescAndRating_monthDesc(self, fide_id: int) -> Player | None: ...

    def findByFed(self, fed: str) -> list[Player]: ...

    def findByFide_idOrderByRating_yearAscAndRating_monthAsc(self, fide_id: int) -> list[Player]: ...

    def countByFide_idAndRating_yearAndRating_month(
        self, fide_id: int, rating_year: int, rating_month: int
    ) -> int: ...

    def countByRating_yearAndRating_month(self, rating_year: int, rating_month: int) -> int: ...

    def findMaxRating_year(self) -> int | None: ...

    def findMaxRating_monthByRating_year(self, rating_year: int) -> int | None: ...

    def findByRating_yearAndRating_monthOrderByStandard_ratingDesc(
        self, rating_year: int, rating_month: int, pageable: Pageable
    ) -> list[Player]: ...

    def findByRating_yearAndRating_monthAndFedOrderByStandard_ratingDesc(
        self, rating_year: int, rating_month: int, fed: str, pageable: Pageable
    ) -> list[Player]: ...

    def findDistinctFedByRating_yearAndRating_monthAndFedIsNotNull(
        self, rating_year: int, rating_month: int
    ) -> list[str]: ...
