from dataclasses import dataclass
from typing import Annotated

from micronaut.data.annotation import GeneratedValue, Id, MappedEntity, Query
from micronaut.data.jdbc.annotation import JdbcRepository
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
    @Query(
        "SELECT * FROM player "
        "WHERE fide_id = :fideId AND rating_year = :ratingYear AND rating_month = :ratingMonth"
    )
    def find_by_fide_id_and_period(
        self, fideId: int, ratingYear: int, ratingMonth: int
    ) -> Player | None: ...

    @Query(
        "SELECT * FROM player WHERE fide_id = :fideId "
        "ORDER BY rating_year DESC, rating_month DESC LIMIT 1"
    )
    def find_latest_by_fide_id(self, fideId: int) -> Player | None: ...

    @Query("SELECT * FROM player WHERE fed = :fed")
    def find_by_fed(self, fed: str) -> list[Player]: ...

    @Query("SELECT * FROM player WHERE fide_id = :fideId ORDER BY rating_year, rating_month")
    def find_all_by_fide_id(self, fideId: int) -> list[Player]: ...

    @Query(
        "SELECT COUNT(*) FROM player "
        "WHERE fide_id = :fideId AND rating_year = :ratingYear AND rating_month = :ratingMonth"
    )
    def count_by_fide_id_and_period(self, fideId: int, ratingYear: int, ratingMonth: int) -> int: ...

    @Query("SELECT MAX(rating_year) FROM player")
    def find_latest_rating_year(self) -> int | None: ...

    @Query("SELECT MAX(rating_month) FROM player WHERE rating_year = :ratingYear")
    def find_latest_rating_month(self, ratingYear: int) -> int | None: ...

    @Query("SELECT COUNT(*) FROM player WHERE rating_year = :ratingYear AND rating_month = :ratingMonth")
    def count_by_period(self, ratingYear: int, ratingMonth: int) -> int: ...
