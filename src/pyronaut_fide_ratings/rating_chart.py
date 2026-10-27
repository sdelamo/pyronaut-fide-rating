from dataclasses import dataclass

import pygal
from micronaut.serde.annotation import Serdeable

from .player import Player

SEX = {"M": "Male", "F": "Female"}


@Serdeable
@dataclass
class RatingCard:
    label: str
    value: str


@Serdeable
@dataclass
class ProfileModel:
    """Model for the profile.jinja view."""
    name: str
    period: str
    fide_id: int
    federation: str
    gender: str
    born: str
    title: str
    ratings: list[RatingCard]
    chart: str


def _rating(value: int) -> int | None:
    # FIDE lists a 0 rating for a category the player is not rated in; draw a gap instead
    return value or None


def render_progress_chart(history: list[Player]) -> str:
    """Line chart of a player's standard, rapid and blitz ratings, one point per rating list."""
    history = sorted(history, key=lambda p: (p.rating_year, p.rating_month))  # oldest left, latest right
    chart = pygal.Line(
        title="Rating progress",
        x_label_rotation=45,
        show_minor_x_labels=False,
        js=[],  # no external scripts: the SVG is self-contained
        disable_xml_declaration=True,
    )
    chart.x_labels = [f"{p.rating_year}-{p.rating_month:02d}" for p in history]
    # one label per January keeps a long history readable; the latest list always gets one too
    chart.x_labels_major = [label for label in chart.x_labels if label.endswith("-01")] + chart.x_labels[-1:]
    chart.add("Standard", [_rating(p.standard_rating) for p in history])
    chart.add("Rapid", [_rating(p.rapid_rating) for p in history])
    chart.add("Blitz", [_rating(p.blitz_rating) for p in history])
    return chart.render(is_unicode=True)


def profile_model(history: list[Player]) -> ProfileModel:
    """The player's latest details and the progress chart, ready for the profile.jinja view."""
    latest = history[-1]
    titles = [t for t in (latest.title, latest.w_title) if t]
    return ProfileModel(
        name=latest.name or f"Player {latest.fide_id}",
        period=f"{latest.rating_year}-{latest.rating_month:02d}",
        fide_id=latest.fide_id,
        federation=latest.fed or "-",
        gender=SEX.get(latest.sex or "", latest.sex or "-"),
        born=str(latest.birth_year) if latest.birth_year else "-",
        title=" / ".join(titles),
        ratings=[
            RatingCard("Standard", str(latest.standard_rating or "Unrated")),
            RatingCard("Rapid", str(latest.rapid_rating or "Unrated")),
            RatingCard("Blitz", str(latest.blitz_rating or "Unrated")),
        ],
        chart=render_progress_chart(history),
    )
