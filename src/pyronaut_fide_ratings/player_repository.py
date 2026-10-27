from micronaut.data.annotation import Query
from micronaut.data.jdbc.annotation import JdbcRepository
from micronaut.data.model.query.builder.sql import Dialect
from micronaut.data.repository import CrudRepository

from .player import Player


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
