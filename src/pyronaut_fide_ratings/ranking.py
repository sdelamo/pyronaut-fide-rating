from dataclasses import dataclass

from micronaut.serde.annotation import Serdeable

from .federation import federation_flag
from .player import Player


@Serdeable
@dataclass
class TopPlayer:
    rank: int
    link: str  # the template can't read snake_case properties of nested items
    name: str
    federation: str
    rating: int


def top_players(players: list[Player]) -> list[TopPlayer]:
    """Rows for the "top players" table, ranked in the order given."""
    return [
        TopPlayer(
            rank,
            f"/fide/ratings/{p.fide_id}",
            p.name or f"Player {p.fide_id}",
            f"{federation_flag(p.fed or '')} {p.fed or '-'}".strip(),
            p.standard_rating,
        )
        for rank, p in enumerate(players, start=1)
    ]
