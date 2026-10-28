import pytest

from micronaut.data.model import Pageable
from pyronaut.test import *
from pyronaut_fide_ratings.player import Player, PlayerRepository


@pytest.fixture
def my_context(request):
    fixture = micronaut_test_fixture(
        request, MicronautTest(environments=["test"], transactional=False)
    )
    yield fixture
    fixture.stop()


@pytest.fixture
def repository(my_context):
    return my_context.get_bean(PlayerRepository)


def player(fide_id: int, year: int = 2026, month: int = 10, **fields) -> Player:
    fields.setdefault("name", f"Player {fide_id}")
    return Player(fide_id=fide_id, rating_year=year, rating_month=month, **fields)


def save_all(repository, *players: Player) -> None:
    for entry in players:
        repository.save(entry)


def test_find_by_fide_id_and_period(repository):
    save_all(repository, player(1, 2026, 9, standard_rating=1500), player(1, 2026, 10, standard_rating=1600))

    found = repository.findByFide_idAndRating_yearAndRating_month(1, 2026, 9)

    assert found is not None and found.standard_rating == 1500
    assert repository.findByFide_idAndRating_yearAndRating_month(1, 2026, 8) is None
    assert repository.findByFide_idAndRating_yearAndRating_month(2, 2026, 9) is None


def test_find_latest_by_fide_id(repository):
    save_all(
        repository,
        player(1, 2025, 12, standard_rating=1400),
        player(1, 2026, 9, standard_rating=1500),
        player(1, 2026, 10, standard_rating=1600),
        player(2, 2027, 1, standard_rating=2000),
    )

    latest = repository.findFirstByFide_idOrderByRating_yearDescAndRating_monthDesc(1)

    assert latest is not None and (latest.rating_year, latest.rating_month) == (2026, 10)
    assert repository.findFirstByFide_idOrderByRating_yearDescAndRating_monthDesc(99) is None


def test_find_latest_by_fide_id_prefers_the_later_year_over_the_later_month(repository):
    save_all(repository, player(1, 2025, 12), player(1, 2026, 1))

    latest = repository.findFirstByFide_idOrderByRating_yearDescAndRating_monthDesc(1)

    assert (latest.rating_year, latest.rating_month) == (2026, 1)


def test_find_by_fed(repository):
    save_all(repository, player(1, fed="ESP"), player(2, fed="GER"), player(3, fed="ESP"), player(4))

    spanish = repository.findByFed("ESP")

    assert sorted(p.fide_id for p in spanish) == [1, 3]
    assert repository.findByFed("FRA") == []


def test_find_all_by_fide_id_is_oldest_first(repository):
    save_all(
        repository,
        player(1, 2026, 10),
        player(1, 2025, 12),
        player(1, 2026, 1),
        player(2, 2020, 1),
    )

    history = repository.findByFide_idOrderByRating_yearAscAndRating_monthAsc(1)

    assert [(p.rating_year, p.rating_month) for p in history] == [(2025, 12), (2026, 1), (2026, 10)]
    assert repository.findByFide_idOrderByRating_yearAscAndRating_monthAsc(99) == []


def test_count_by_fide_id_and_period(repository):
    save_all(repository, player(1, 2026, 10), player(1, 2026, 9), player(2, 2026, 10))

    assert repository.countByFide_idAndRating_yearAndRating_month(1, 2026, 10) == 1
    assert repository.countByFide_idAndRating_yearAndRating_month(1, 2026, 8) == 0
    assert repository.countByFide_idAndRating_yearAndRating_month(3, 2026, 10) == 0


def test_find_latest_rating_year_and_month(repository):
    assert repository.findMaxRating_year() is None
    assert repository.findMaxRating_monthByRating_year(2026) is None
    save_all(repository, player(1, 2025, 12), player(2, 2026, 3), player(3, 2026, 10), player(4, 2026, 7))

    assert repository.findMaxRating_year() == 2026
    assert repository.findMaxRating_monthByRating_year(2026) == 10  # latest month of that year
    assert repository.findMaxRating_monthByRating_year(2025) == 12
    assert repository.findMaxRating_monthByRating_year(2024) is None


def test_count_by_period(repository):
    save_all(repository, player(1, 2026, 10), player(2, 2026, 10), player(3, 2026, 9))

    assert repository.countByRating_yearAndRating_month(2026, 10) == 2
    assert repository.countByRating_yearAndRating_month(2026, 9) == 1
    assert repository.countByRating_yearAndRating_month(2026, 8) == 0


def test_find_top_by_standard_rating(repository):
    save_all(
        repository,
        player(1, standard_rating=2500),
        player(2, standard_rating=2700),
        player(3, standard_rating=2600),
        player(4, 2026, 9, standard_rating=2900),  # another period
    )

    top = repository.findByRating_yearAndRating_monthOrderByStandard_ratingDesc(2026, 10, Pageable.from_(0, 2))

    assert [p.fide_id for p in top] == [2, 3]  # highest first, limited, this period only
    assert [p.fide_id for p in repository.findByRating_yearAndRating_monthOrderByStandard_ratingDesc(2026, 10, Pageable.from_(0, 10))] == [2, 3, 1]
    assert repository.findByRating_yearAndRating_monthOrderByStandard_ratingDesc(2026, 8, Pageable.from_(0, 10)) == []


def test_find_top_by_federation_and_standard_rating(repository):
    save_all(
        repository,
        player(1, fed="ESP", standard_rating=2400),
        player(2, fed="ESP", standard_rating=2600),
        player(3, fed="GER", standard_rating=2800),
        player(4, fed="ESP", standard_rating=2500),
        player(5, 2026, 9, fed="ESP", standard_rating=2900),  # another period
    )

    top = repository.findByRating_yearAndRating_monthAndFedOrderByStandard_ratingDesc(2026, 10, "ESP", Pageable.from_(0, 2))

    assert [p.fide_id for p in top] == [2, 4]
    assert repository.findByRating_yearAndRating_monthAndFedOrderByStandard_ratingDesc(2026, 10, "FRA", Pageable.from_(0, 10)) == []


def test_find_federations(repository):
    save_all(
        repository,
        player(1, fed="ESP"),
        player(2, fed="ESP"),
        player(3, fed="GER"),
        player(4),  # no federation
        player(5, 2026, 9, fed="FRA"),  # another period
    )

    assert sorted(repository.findDistinctFedByRating_yearAndRating_monthAndFedIsNotNull(2026, 10)) == ["ESP", "GER"]
    assert repository.findDistinctFedByRating_yearAndRating_monthAndFedIsNotNull(2026, 8) == []
